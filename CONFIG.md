# Config Documentation

This page documents configuration values and what they do. You begin with an empty configuration file.  
You may alter your configuration with `unshackle cfg --help`, or find the direct location with `unshackle env info`.  
Configuration values are listed in alphabetical order.

Avoid putting comments in the config file as they may be removed. Comments are currently kept only thanks
to the usage of `ruamel.yaml` to parse and write YAML files. In the future `yaml` may be used instead,
which does not keep comments.

## aria2c (dict)

- `max_concurrent_downloads`
  Maximum number of parallel downloads. Default: `min(32,(cpu_count+4))`  
  Note: Overrides the `max_workers` parameter of the aria2(c) downloader function.
- `max_connection_per_server`
  Maximum number of connections to one server for each download. Default: `1`
- `split`
  Split a file into N chunks and download each chunk on its own connection. Default: `5`
- `file_allocation`
  Specify file allocation method. Default: `"prealloc"`

  - `"none"` doesn't pre-allocate file space.
  - `"prealloc"` pre-allocates file space before download begins. This may take some time depending on the size of the
    file.
  - `"falloc"` is your best choice if you are using newer file systems such as ext4 (with extents support), btrfs, xfs
    or NTFS (MinGW build only). It allocates large(few GiB) files almost instantly. Don't use falloc with legacy file
    systems such as ext3 and FAT32 because it takes almost same time as prealloc, and it blocks aria2 entirely until
    allocation finishes. falloc may not be available if your system doesn't have posix_fallocate(3) function.
  - `"trunc"` uses ftruncate(2) system call or platform-specific counterpart to truncate a file to a specified length.

## cdm (dict)

Pre-define which Widevine or PlayReady device to use for each Service by Service Tag as Key (case-sensitive).  
The value should be a WVD or PRD filename without the file extension. When
loading the device, unshackle will look in both the `WVDs` and `PRDs` directories
for a matching file.

For example,

```yaml
AMZN: chromecdm_903_l3
NF: nexus_6_l1
```

You may also specify this device based on the profile used.

For example,

```yaml
AMZN: chromecdm_903_l3
NF: nexus_6_l1
DSNP:
  john_sd: chromecdm_903_l3
  jane_uhd: nexus_5_l1
```

You can also specify a fallback value to predefine if a match was not made.  
This can be done using `default` key. This can help reduce redundancy in your specifications.

For example, the following has the same result as the previous example, as well as all other
services and profiles being pre-defined to use `chromecdm_903_l3`.

```yaml
NF: nexus_6_l1
DSNP:
  jane_uhd: nexus_5_l1
default: chromecdm_903_l3
```

## chapter_fallback_name (str)

The Chapter Name to use when exporting a Chapter without a Name.
The default is no fallback name at all and no Chapter name will be set.

The fallback name can use the following variables in f-string style:

- `{i}`: The Chapter number starting at 1.
  E.g., `"Chapter {i}"`: "Chapter 1", "Intro", "Chapter 3".
- `{j}`: A number starting at 1 that increments any time a Chapter has no title.
  E.g., `"Chapter {j}"`: "Chapter 1", "Intro", "Chapter 2".

These are formatted with f-strings, directives are supported.
For example, `"Chapter {i:02}"` will result in `"Chapter 01"`.

## credentials (dict[str, str|list|dict])

Specify login credentials to use for each Service, and optionally per-profile.

For example,

```yaml
ALL4: jane@gmail.com:LoremIpsum100 # directly
AMZN: # or per-profile, optionally with a default
  default: jane@example.tld:LoremIpsum99 # <-- used by default if -p/--profile is not used
  james: james@gmail.com:TheFriend97
  john: john@example.tld:LoremIpsum98
NF: # the `default` key is not necessary, but no credential will be used by default
  john: john@gmail.com:TheGuyWhoPaysForTheNetflix69420
```

The value should be in string form, i.e. `john@gmail.com:password123` or `john:password123`.  
Any arbitrary values can be used on the left (username/password/phone) and right (password/secret).  
You can also specify these in list form, i.e., `["john@gmail.com", ":PasswordWithAColon"]`.

If you specify multiple credentials with keys like the `AMZN` and `NF` example above, then you should
use a `default` key or no credential will be loaded automatically unless you use `-p/--profile`. You
do not have to use a `default` key at all.

Please be aware that this information is sensitive and to keep it safe. Do not share your config.

## curl_impersonate (dict)

- `browser` - The Browser to impersonate as. A list of available Browsers and Versions are listed here:
  <https://github.com/yifeikong/curl_cffi#sessions>

  Default: `"chrome124"`

For example,

```yaml
curl_impersonate:
  browser: "chrome120"
```

## directories (dict)

Override the default directories used across unshackle.  
The directories are set to common values by default.

The following directories are available and may be overridden,

- `commands` - CLI Command Classes.
- `services` - Service Classes.
- `vaults` - Vault Classes.
- `fonts` - Font files (ttf or otf).
- `downloads` - Downloads.
- `temp` - Temporary files or conversions during download.
- `cache` - Expiring data like Authorization tokens, or other misc data.
- `cookies` - Expiring Cookie data.
- `logs` - Logs.
- `wvds` - Widevine Devices.
- `prds` - PlayReady Devices.
- `dcsl` - Device Certificate Status List.

Notes:

- `services` accepts either a single directory or a list of directories to search for service modules.

For example,

```yaml
downloads: "D:/Downloads/unshackle"
temp: "D:/Temp/unshackle"
```

There are directories not listed that cannot be modified as they are crucial to the operation of unshackle.

## dl (dict)

Pre-define default options and switches of the `dl` command.  
The values will be ignored if explicitly set in the CLI call.

The Key must be the same value Python click would resolve it to as an argument.  
E.g., `@click.option("-r", "--range", "range_", type=...` actually resolves as `range_` variable.

For example to set the default primary language to download to German,

```yaml
lang: de
```

You can also set multiple preferred languages using a list, e.g.,

```yaml
lang:
  - en
  - fr
```

to set how many tracks to download concurrently to 4 and download threads to 16,

```yaml
downloads: 4
workers: 16
```

to set `--bitrate=CVBR` for the AMZN service,

```yaml
lang: de
AMZN:
  bitrate: CVBR
```

or to change the output subtitle format from the default (original format) to WebVTT,

```yaml
sub_format: vtt
```

## downloader (str | dict)

Choose what software to use to download data throughout unshackle where needed.
You may provide a single downloader globally or a mapping of service tags to
downloaders.

Options:

- `requests` (default) - <https://github.com/psf/requests>
- `aria2c` - <https://github.com/aria2/aria2>
- `curl_impersonate` - <https://github.com/yifeikong/curl-impersonate> (via <https://github.com/yifeikong/curl_cffi>)
- `n_m3u8dl_re` - <https://github.com/nilaoda/N_m3u8DL-RE>

Note that aria2c can reach the highest speeds as it utilizes threading and more connections than the other downloaders. However, aria2c can also be one of the more unstable downloaders. It will work one day, then not another day. It also does not support HTTP(S) proxies while the other downloaders do.

Example mapping:

```yaml
downloader:
  NF: requests
  AMZN: n_m3u8dl_re
  DSNP: n_m3u8dl_re
  default: requests
```

The `default` entry is optional. If omitted, `requests` will be used for services not listed.

## decryption (str | dict)

Choose what software to use to decrypt DRM-protected content throughout unshackle where needed.
You may provide a single decryption method globally or a mapping of service tags to
decryption methods.

Options:

- `shaka` (default) - Shaka Packager - <https://github.com/shaka-project/shaka-packager>
- `mp4decrypt` - mp4decrypt from Bento4 - <https://github.com/axiomatic-systems/Bento4>

Note that Shaka Packager is the traditional method and works with most services. mp4decrypt
is an alternative that may work better with certain services that have specific encryption formats.

Example mapping:

```yaml
decryption:
  ATVP: mp4decrypt
  AMZN: shaka
  default: shaka
```

The `default` entry is optional. If omitted, `shaka` will be used for services not listed.

Simple configuration (single method for all services):

```yaml
decryption: mp4decrypt
```

## filenames (dict)

Override the default filenames used across unshackle.  
The filenames use various variables that are replaced during runtime.

The following filenames are available and may be overridden:

- `log` - Log filenames. Uses `{name}` and `{time}` variables.
- `config` - Service configuration filenames.
- `root_config` - Root configuration filename.
- `chapters` - Chapter export filenames. Uses `{title}` and `{random}` variables.
- `subtitle` - Subtitle export filenames. Uses `{id}` and `{language}` variables.

For example,

```yaml
filenames:
  log: "unshackle_{name}_{time}.log"
  config: "config.yaml"
  root_config: "unshackle.yaml"
  chapters: "Chapters_{title}_{random}.txt"
  subtitle: "Subtitle_{id}_{language}.srt"
```

## headers (dict)

Case-Insensitive dictionary of headers that all Services begin their Request Session state with.  
All requests will use these unless changed explicitly or implicitly via a Server response.  
These should be sane defaults and anything that would only be useful for some Services should not
be put here.

Avoid headers like 'Accept-Encoding' as that would be a compatibility header that Python-requests will
set for you.

I recommend using,

```yaml
Accept-Language: "en-US,en;q=0.8"
User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36"
```

## key_vaults (list\[dict])

Key Vaults store your obtained Content Encryption Keys (CEKs) and Key IDs per-service.

This can help reduce unnecessary License calls even during the first download. This is because a Service may
provide the same Key ID and CEK for both Video and Audio, as well as for multiple resolutions or bitrates.

You can have as many Key Vaults as you would like. It's nice to share Key Vaults or use a unified Vault on
Teams as sharing CEKs immediately can help reduce License calls drastically.

Three types of Vaults are in the Core codebase, API, SQLite and MySQL. API makes HTTP requests to a RESTful API,
whereas SQLite and MySQL directly connect to an SQLite or MySQL Database.

Note: SQLite and MySQL vaults have to connect directly to the Host/IP. It cannot be in front of a PHP API or such.
Beware that some Hosting Providers do not let you access the MySQL server outside their intranet and may not be
accessible outside their hosting platform.

Additional behavior:

- `no_push` (bool): Optional per-vault flag. When `true`, the vault will not receive pushed keys (writes) but
  will still be queried and can provide keys for lookups. Useful for read-only/backup vaults.

### Using an API Vault

API vaults use a specific HTTP request format, therefore API or HTTP Key Vault APIs from other projects or services may
not work in unshackle. The API format can be seen in the [API Vault Code](unshackle/vaults/API.py).

```yaml
- type: API
  name: "John#0001's Vault" # arbitrary vault name
  uri: "https://key-vault.example.com" # api base uri (can also be an IP or IP:Port)
  # uri: "127.0.0.1:80/key-vault"
  # uri: "https://api.example.com/key-vault"
  token: "random secret key" # authorization token
  # no_push: true            # optional; make this API vault read-only (lookups only)
```

### Using a MySQL Vault

MySQL vaults can be either MySQL or MariaDB servers. I recommend MariaDB.  
A MySQL Vault can be on a local or remote network, but I recommend SQLite for local Vaults.

```yaml
- type: MySQL
  name: "John#0001's Vault" # arbitrary vault name
  host: "127.0.0.1" # host/ip
  # port: 3306               # port (defaults to 3306)
  database: vault # database used for unshackle
  username: jane11
  password: Doe123
  # no_push: false           # optional; defaults to false
```

I recommend giving only a trustable user (or yourself) CREATE permission and then use unshackle to cache at least one CEK
per Service to have it create the tables. If you don't give any user permissions to create tables, you will need to
make tables yourself.

- Use a password on all user accounts.
- Never use the root account with unshackle (even if it's you).
- Do not give multiple users the same username and/or password.
- Only give users access to the database used for unshackle.
- You may give trusted users CREATE permission so unshackle can create tables if needed.
- Other uses should only be given SELECT and INSERT permissions.

### Using an SQLite Vault

SQLite Vaults are usually only used for locally stored vaults. This vault may be stored on a mounted Cloud storage
drive, but I recommend using SQLite exclusively as an offline-only vault. Effectively this is your backup vault in
case something happens to your MySQL Vault.

```yaml
- type: SQLite
  name: "My Local Vault" # arbitrary vault name
  path: "C:/Users/Jane11/Documents/unshackle/data/key_vault.db"
  # no_push: true           # optional; commonly true for local backup vaults
```

**Note**: You do not need to create the file at the specified path.  
SQLite will create a new SQLite database at that path if one does not exist.  
Try not to accidentally move the `db` file once created without reflecting the change in the config, or you will end
up with multiple databases.

If you work on a Team I recommend every team member having their own SQLite Vault even if you all use a MySQL vault
together.

## muxing (dict)

- `set_title`
  Set the container title to `Show SXXEXX Episode Name` or `Movie (Year)`. Default: `true`

## n_m3u8dl_re (dict)

Configuration for N_m3u8DL-RE downloader. This downloader is particularly useful for HLS streams.

- `thread_count`
  Number of threads to use for downloading. Default: Uses the same value as max_workers from the command.
- `ad_keyword`
  Keyword to identify and potentially skip advertisement segments. Default: `None`
- `use_proxy`
  Whether to use proxy when downloading. Default: `true`

For example,

```yaml
n_m3u8dl_re:
  thread_count: 16
  ad_keyword: "advertisement"
  use_proxy: true
```

## nordvpn (dict)

**Legacy configuration. Use `proxy_providers.nordvpn` instead.**

Set your NordVPN Service credentials with `username` and `password` keys to automate the use of NordVPN as a Proxy
system where required.

You can also specify specific servers to use per-region with the `server_map` key.  
Sometimes a specific server works best for a service than others, so hard-coding one for a day or two helps.

For example,

```yaml
nordvpn:
  username: zxqsR7C5CyGwmGb6KSvk8qsZ # example of the login format
  password: wXVHmht22hhRKUEQ32PQVjCZ
  server_map:
    us: 12 # force US server #12 for US proxies
```

The username and password should NOT be your normal NordVPN Account Credentials.  
They should be the `Service credentials` which can be found on your Nord Account Dashboard.

Note that `gb` is used instead of `uk` to be more consistent across regional systems.

## proxy_providers (dict)

Enable external proxy provider services. These proxies will be used automatically where needed as defined by the
Service's GEOFENCE class property, but can also be explicitly used with `--proxy`. You can specify which provider
to use by prefixing it with the provider key name, e.g., `--proxy basic:de` or `--proxy nordvpn:de`. Some providers
support specific query formats for selecting a country/server.

### basic (dict[str, str|list])

Define a mapping of country to proxy to use where required.  
The keys are region Alpha 2 Country Codes. Alpha 2 Country Codes are `[a-z]{2}` codes, e.g., `us`, `gb`, and `jp`.  
Don't get this mixed up with language codes like `en` vs. `gb`, or `ja` vs. `jp`.

Do note that each key's value can be a list of strings, or a string. For example,

```yaml
us:
  - "http://john%40email.tld:password123@proxy-us.domain.tld:8080"
  - "http://jane%40email.tld:password456@proxy-us.domain2.tld:8080"
de: "https://127.0.0.1:8080"
```

Note that if multiple proxies are defined for a region, then by default one will be randomly chosen.
You can choose a specific one by specifying it's number, e.g., `--proxy basic:us2` will choose the
second proxy of the US list.

### nordvpn (dict)

Set your NordVPN Service credentials with `username` and `password` keys to automate the use of NordVPN as a Proxy
system where required.

You can also specify specific servers to use per-region with the `server_map` key.  
Sometimes a specific server works best for a service than others, so hard-coding one for a day or two helps.

For example,

```yaml
username: zxqsR7C5CyGwmGb6KSvk8qsZ # example of the login format
password: wXVHmht22hhRKUEQ32PQVjCZ
server_map:
  us: 12 # force US server #12 for US proxies
```

The username and password should NOT be your normal NordVPN Account Credentials.  
They should be the `Service credentials` which can be found on your Nord Account Dashboard.

Once set, you can also specifically opt in to use a NordVPN proxy by specifying `--proxy=gb` or such.
You can even set a specific server number this way, e.g., `--proxy=gb2366`.

Note that `gb` is used instead of `uk` to be more consistent across regional systems.

### surfsharkvpn (dict)

Enable Surfshark VPN proxy service using Surfshark Service credentials (not your login password).  
You may pin specific server IDs per region using `server_map`.

```yaml
username: your_surfshark_service_username # https://my.surfshark.com/vpn/manual-setup/main/openvpn
password: your_surfshark_service_password # service credentials, not account password
server_map:
  us: 3844 # force US server #3844
  gb: 2697 # force GB server #2697
  au: 4621 # force AU server #4621
```

### hola (dict)

Enable Hola VPN proxy service. This is a simple provider that doesn't require configuration.

For example,

```yaml
proxy_providers:
  hola: {}
```

Note: Hola VPN is automatically enabled when proxy_providers is configured, no additional setup is required.

## remote_cdm (list\[dict])

Use [pywidevine] Serve-compliant Remote CDMs in unshackle as if it was a local widevine device file.  
The name of each defined device maps as if it was a local device and should be used like a local device.

For example,

```yaml
- name: chromecdm_903_l3 # name must be unique for each remote CDM
  # the device type, system id and security level must match the values of the device on the API
  # if any of the information is wrong, it will raise an error, if you do not know it ask the API owner
  device_type: CHROME
  system_id: 1234
  security_level: 3
  host: "http://xxxxxxxxxxxxxxxx/the_cdm_endpoint"
  secret: "secret/api key"
  device_name: "remote device to use" # the device name from the API, usually a wvd filename
```

[pywidevine]: https://github.com/rlaphoenix/pywidevine

## scene_naming (bool)

Set scene-style naming for titles. When `true` uses scene naming patterns (e.g., `Prime.Suspect.S07E01...`), when
`false` uses a more human-readable style (e.g., `Prime Suspect S07E01 ...`). Default: `true`.

## series_year (bool)

Whether to include the series year in series names for episodes and folders. Default: `true`.

## serve (dict)

Configuration data for pywidevine's serve functionality run through unshackle.
This effectively allows you to run `unshackle serve` to start serving pywidevine Serve-compliant CDMs right from your
local widevine device files.

For example,

```yaml
users:
  secret_key_for_jane: # 32bit hex recommended, case-sensitive
    devices: # list of allowed devices for this user
      - generic_nexus_4464_l3
    username: jane # only for internal logging, users will not see this name
  secret_key_for_james:
    devices:
      - generic_nexus_4464_l3
    username: james
  secret_key_for_john:
    devices:
      - generic_nexus_4464_l3
    username: john
# devices can be manually specified by path if you don't want to add it to
# unshackle's WVDs directory for whatever reason
# devices:
#   - 'C:\Users\john\Devices\test_devices_001.wvd'
```

## services (dict)

Configuration data for each Service. The Service will have the data within this section merged into the `config.yaml`
before provided to the Service class.

Think of this config to be used for more sensitive configuration data, like user or device-specific API keys, IDs,
device attributes, and so on. A `config.yaml` file is typically shared and not meant to be modified, so use this for
any sensitive configuration data.

The Key is the Service Tag, but can take any arbitrary form for its value. It's expected to begin as either a list or
a dictionary.

For example,

```yaml
NOW:
  client:
    auth_scheme: MESSO
    # ... more sensitive data
```

## set_terminal_bg (bool)

Controls whether unshackle should set the terminal background color. Default: `false`

For example,

```yaml
set_terminal_bg: true
```

## tag (str)

Group or Username to postfix to the end of all download filenames following a dash.  
For example, `tag: "J0HN"` will have `-J0HN` at the end of all download filenames.

## tag_group_name (bool)

Enable/disable tagging downloads with your group name when `tag` is set. Default: `true`.

## tag_imdb_tmdb (bool)

Enable/disable tagging downloaded files with IMDB/TMDB/TVDB identifiers (when available). Default: `true`.

## title_cache_enabled (bool)

Enable/disable caching of title metadata to reduce redundant API calls. Default: `true`.

## title_cache_time (int)

Cache duration in seconds for title metadata. Default: `1800` (30 minutes).

## title_cache_max_retention (int)

Maximum retention time in seconds for serving slightly stale cached title metadata when API calls fail.  
Default: `86400` (24 hours). Effective retention is `min(title_cache_time + grace, title_cache_max_retention)`.

## tmdb_api_key (str)

API key for The Movie Database (TMDB). This is used for tagging downloaded files with TMDB,
IMDB and TVDB identifiers. Leave empty to disable automatic lookups.

To obtain a TMDB API key:

1. Create an account at <https://www.themoviedb.org/>
2. Go to <https://www.themoviedb.org/settings/api> to register for API access
3. Fill out the API application form with your project details
4. Once approved, you'll receive your API key

For example,

```yaml
tmdb_api_key: cf66bf18956kca5311ada3bebb84eb9a # Not a real key
```

**Note**: Keep your API key secure and do not share it publicly. This key is used by the core/utils/tags.py module to fetch metadata from TMDB for proper file tagging.

## subtitle (dict)

Control subtitle conversion and SDH (hearing-impaired) stripping behavior.

- `conversion_method`: How to convert subtitles between formats. Default: `auto`.

  - `auto`: Use subby for WebVTT/SAMI, standard for others.
  - `subby`: Always use subby with CommonIssuesFixer.
  - `subtitleedit`: Prefer SubtitleEdit when available; otherwise fallback to standard conversion.
  - `pycaption`: Use only the pycaption library (no SubtitleEdit, no subby).

- `sdh_method`: How to strip SDH cues. Default: `auto`.
  - `auto`: Try subby for SRT first, then SubtitleEdit, then filter-subs.
  - `subby`: Use subby’s SDHStripper (SRT only).
  - `subtitleedit`: Use SubtitleEdit’s RemoveTextForHI when available.
  - `filter-subs`: Use the subtitle-filter library.

Example:

```yaml
subtitle:
  conversion_method: auto
  sdh_method: auto
```

## update_checks (bool)

Check for updates from the GitHub repository on startup. Default: `true`.

## update_check_interval (int)

How often to check for updates, in hours. Default: `24`.
