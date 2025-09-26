from __future__ import annotations

import logging
import os
import re
import subprocess
import tempfile
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional, Tuple
from xml.sax.saxutils import escape

import requests
from requests.adapters import HTTPAdapter, Retry

from unshackle.core import binaries
from unshackle.core.config import config
from unshackle.core.titles.episode import Episode
from unshackle.core.titles.movie import Movie
from unshackle.core.titles.title import Title

STRIP_RE = re.compile(r"[^a-z0-9]+", re.I)
YEAR_RE = re.compile(r"\s*\(?[12][0-9]{3}\)?$")
HEADERS = {"User-Agent": "unshackle-tags/1.0"}


log = logging.getLogger("TAGS")


def _get_session() -> requests.Session:
    """Create a requests session with retry logic for network failures."""
    session = requests.Session()
    session.headers.update(HEADERS)

    retry = Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def _api_key() -> Optional[str]:
    return config.tmdb_api_key or os.getenv("TMDB_API_KEY")


def _clean(s: str) -> str:
    return STRIP_RE.sub("", s).lower()


def _strip_year(s: str) -> str:
    return YEAR_RE.sub("", s).strip()


def fuzzy_match(a: str, b: str, threshold: float = 0.8) -> bool:
    """Return True if ``a`` and ``b`` are a close match."""

    ratio = SequenceMatcher(None, _clean(a), _clean(b)).ratio()
    return ratio >= threshold


def search_simkl(title: str, year: Optional[int], kind: str) -> Tuple[Optional[dict], Optional[str], Optional[int]]:
    """Search Simkl API for show information by filename (no auth required)."""
    log.debug("Searching Simkl for %r (%s, %s)", title, kind, year)

    # Construct appropriate filename based on type
    filename = f"{title}"
    if year:
        filename = f"{title} {year}"

    if kind == "tv":
        filename += " S01E01.mkv"
    else:  # movie
        filename += " 2160p.mkv"

    try:
        session = _get_session()
        resp = session.post("https://api.simkl.com/search/file", json={"file": filename}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        log.debug("Simkl API response received")

        # Handle case where SIMKL returns empty list (no results)
        if isinstance(data, list):
            log.debug("Simkl returned list (no matches) for %r", filename)
            return None, None, None

        # Handle TV show responses
        if data.get("type") == "episode" and "show" in data:
            show_info = data["show"]
            show_title = show_info.get("title")
            show_year = show_info.get("year")

            # Verify title matches and year if provided
            if not fuzzy_match(show_title, title):
                log.debug("Simkl title mismatch: searched %r, got %r", title, show_title)
                return None, None, None
            if year and show_year and abs(year - show_year) > 1:  # Allow 1 year difference
                log.debug("Simkl year mismatch: searched %d, got %d", year, show_year)
                return None, None, None

            tmdb_id = show_info.get("ids", {}).get("tmdbtv")
            if tmdb_id:
                tmdb_id = int(tmdb_id)
            log.debug("Simkl -> %s (TMDB ID %s)", show_title, tmdb_id)
            return data, show_title, tmdb_id

        # Handle movie responses
        elif data.get("type") == "movie" and "movie" in data:
            movie_info = data["movie"]
            movie_title = movie_info.get("title")
            movie_year = movie_info.get("year")

            # Verify title matches and year if provided
            if not fuzzy_match(movie_title, title):
                log.debug("Simkl title mismatch: searched %r, got %r", title, movie_title)
                return None, None, None
            if year and movie_year and abs(year - movie_year) > 1:  # Allow 1 year difference
                log.debug("Simkl year mismatch: searched %d, got %d", year, movie_year)
                return None, None, None

            ids = movie_info.get("ids", {})
            tmdb_id = ids.get("tmdb") or ids.get("moviedb")
            if tmdb_id:
                tmdb_id = int(tmdb_id)
            log.debug("Simkl -> %s (TMDB ID %s)", movie_title, tmdb_id)
            return data, movie_title, tmdb_id

    except (requests.RequestException, ValueError, KeyError) as exc:
        log.debug("Simkl search failed: %s", exc)

    return None, None, None


def search_show_info(title: str, year: Optional[int], kind: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """Search for show information, trying Simkl first, then TMDB fallback. Returns (tmdb_id, title, source)."""
    simkl_data, simkl_title, simkl_tmdb_id = search_simkl(title, year, kind)

    if simkl_data and simkl_title and fuzzy_match(simkl_title, title):
        return simkl_tmdb_id, simkl_title, "simkl"

    tmdb_id, tmdb_title = search_tmdb(title, year, kind)
    return tmdb_id, tmdb_title, "tmdb"


def search_tmdb(title: str, year: Optional[int], kind: str) -> Tuple[Optional[int], Optional[str]]:
    api_key = _api_key()
    if not api_key:
        return None, None

    search_title = _strip_year(title)
    log.debug("Searching TMDB for %r (%s, %s)", search_title, kind, year)

    params = {"api_key": api_key, "query": search_title}
    if year is not None:
        params["year" if kind == "movie" else "first_air_date_year"] = year

    try:
        session = _get_session()
        r = session.get(
            f"https://api.themoviedb.org/3/search/{kind}",
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        js = r.json()
        results = js.get("results") or []
        log.debug("TMDB returned %d results", len(results))
        if not results:
            return None, None
    except requests.RequestException as exc:
        log.warning("Failed to search TMDB for %s: %s", title, exc)
        return None, None

    best_ratio = 0.0
    best_id: Optional[int] = None
    best_title: Optional[str] = None
    for result in results:
        candidates = [
            result.get("title"),
            result.get("name"),
            result.get("original_title"),
            result.get("original_name"),
        ]
        candidates = [c for c in candidates if c]  # Filter out None/empty values

        if not candidates:
            continue

        # Find the best matching candidate from all available titles
        for candidate in candidates:
            ratio = SequenceMatcher(None, _clean(search_title), _clean(candidate)).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_id = result.get("id")
                best_title = candidate
    log.debug(
        "Best candidate ratio %.2f for %r (ID %s)",
        best_ratio,
        best_title,
        best_id,
    )

    if best_id is not None:
        return best_id, best_title

    first = results[0]
    return first.get("id"), first.get("title") or first.get("name")


def get_title(tmdb_id: int, kind: str) -> Optional[str]:
    """Fetch the name/title of a TMDB entry by ID."""

    api_key = _api_key()
    if not api_key:
        return None

    try:
        session = _get_session()
        r = session.get(
            f"https://api.themoviedb.org/3/{kind}/{tmdb_id}",
            params={"api_key": api_key},
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Failed to fetch TMDB title: %s", exc)
        return None

    js = r.json()
    return js.get("title") or js.get("name")


def get_year(tmdb_id: int, kind: str) -> Optional[int]:
    """Fetch the release year of a TMDB entry by ID."""

    api_key = _api_key()
    if not api_key:
        return None

    try:
        session = _get_session()
        r = session.get(
            f"https://api.themoviedb.org/3/{kind}/{tmdb_id}",
            params={"api_key": api_key},
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Failed to fetch TMDB year: %s", exc)
        return None

    js = r.json()
    date = js.get("release_date") or js.get("first_air_date")
    if date and len(date) >= 4 and date[:4].isdigit():
        return int(date[:4])
    return None


def external_ids(tmdb_id: int, kind: str) -> dict:
    api_key = _api_key()
    if not api_key:
        return {}
    url = f"https://api.themoviedb.org/3/{kind}/{tmdb_id}/external_ids"
    log.debug("Fetching external IDs for %s %s", kind, tmdb_id)

    try:
        session = _get_session()
        r = session.get(
            url,
            params={"api_key": api_key},
            timeout=30,
        )
        r.raise_for_status()
        js = r.json()
        log.debug("External IDs response: %s", js)
        return js
    except requests.RequestException as exc:
        log.warning("Failed to fetch external IDs for %s %s: %s", kind, tmdb_id, exc)
        return {}


def _apply_tags(path: Path, tags: dict[str, str]) -> None:
    if not tags:
        return
    if not binaries.Mkvpropedit:
        log.debug("mkvpropedit not found on PATH; skipping tags")
        return
    log.debug("Applying tags to %s: %s", path, tags)
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<Tags>", "  <Tag>", "    <Targets/>"]
    for name, value in tags.items():
        xml_lines.append(f"    <Simple><Name>{escape(name)}</Name><String>{escape(value)}</String></Simple>")
    xml_lines.extend(["  </Tag>", "</Tags>"])
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write("\n".join(xml_lines))
        tmp_path = Path(f.name)
    try:
        subprocess.run(
            [str(binaries.Mkvpropedit), str(path), "--tags", f"global:{tmp_path}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log.debug("Tags applied via mkvpropedit")
    finally:
        tmp_path.unlink(missing_ok=True)


def tag_file(path: Path, title: Title, tmdb_id: Optional[int] | None = None) -> None:
    log.debug("Tagging file %s with title %r", path, title)
    standard_tags: dict[str, str] = {}
    custom_tags: dict[str, str] = {}

    if config.tag and config.tag_group_name:
        custom_tags["Group"] = config.tag
    description = getattr(title, "description", None)
    if description:
        if len(description) > 255:
            truncated = description[:255]
            if " " in truncated:
                truncated = truncated.rsplit(" ", 1)[0]
            description = truncated + "..."
        custom_tags["Description"] = description

    if isinstance(title, Movie):
        kind = "movie"
        name = title.name
        year = title.year
    elif isinstance(title, Episode):
        kind = "tv"
        name = title.title
        year = title.year
    else:
        _apply_tags(path, custom_tags)
        return

    if config.tag_imdb_tmdb:
        # If tmdb_id is provided (via --tmdb), skip Simkl and use TMDB directly
        if tmdb_id is not None:
            log.debug("Using provided TMDB ID %s for tags", tmdb_id)
        else:
            # Try Simkl first for automatic lookup
            simkl_data, simkl_title, simkl_tmdb_id = search_simkl(name, year, kind)

            if simkl_data and simkl_title and fuzzy_match(simkl_title, name):
                log.debug("Using Simkl data for tags")
                if simkl_tmdb_id:
                    tmdb_id = simkl_tmdb_id

                # Handle TV show data from Simkl
                if simkl_data.get("type") == "episode" and "show" in simkl_data:
                    show_ids = simkl_data.get("show", {}).get("ids", {})
                    if show_ids.get("imdb"):
                        standard_tags["IMDB"] = show_ids["imdb"]
                    if show_ids.get("tvdb"):
                        standard_tags["TVDB2"] = f"series/{show_ids['tvdb']}"
                    if show_ids.get("tmdbtv"):
                        standard_tags["TMDB"] = f"tv/{show_ids['tmdbtv']}"

                # Handle movie data from Simkl
                elif simkl_data.get("type") == "movie" and "movie" in simkl_data:
                    movie_ids = simkl_data.get("movie", {}).get("ids", {})
                    if movie_ids.get("imdb"):
                        standard_tags["IMDB"] = movie_ids["imdb"]
                    if movie_ids.get("tvdb"):
                        standard_tags["TVDB2"] = f"movies/{movie_ids['tvdb']}"
                    if movie_ids.get("tmdb"):
                        standard_tags["TMDB"] = f"movie/{movie_ids['tmdb']}"

        # Use TMDB API for additional metadata (either from provided ID or Simkl lookup)
        api_key = _api_key()
        if not api_key:
            log.debug("No TMDB API key set; applying basic tags only")
            _apply_tags(path, custom_tags)
            return

        tmdb_title: Optional[str] = None
        if tmdb_id is None:
            tmdb_id, tmdb_title = search_tmdb(name, year, kind)
            log.debug("TMDB search result: %r (ID %s)", tmdb_title, tmdb_id)
            if not tmdb_id or not tmdb_title or not fuzzy_match(tmdb_title, name):
                log.debug("TMDB search did not match; skipping external ID lookup")
                _apply_tags(path, custom_tags)
                return

        prefix = "movie" if kind == "movie" else "tv"
        standard_tags["TMDB"] = f"{prefix}/{tmdb_id}"
        try:
            ids = external_ids(tmdb_id, kind)
        except requests.RequestException as exc:
            log.debug("Failed to fetch external IDs: %s", exc)
            ids = {}
        else:
            log.debug("External IDs found: %s", ids)

        imdb_id = ids.get("imdb_id")
        if imdb_id:
            standard_tags["IMDB"] = imdb_id
        tvdb_id = ids.get("tvdb_id")
        if tvdb_id:
            if kind == "movie":
                standard_tags["TVDB2"] = f"movies/{tvdb_id}"
            else:
                standard_tags["TVDB2"] = f"series/{tvdb_id}"

    merged_tags = {
        **custom_tags,
        **standard_tags,
    }
    _apply_tags(path, merged_tags)


__all__ = [
    "search_simkl",
    "search_show_info",
    "search_tmdb",
    "get_title",
    "get_year",
    "external_ids",
    "tag_file",
    "fuzzy_match",
]
