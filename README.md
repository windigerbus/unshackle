<p align="center">
    <svg xmlns="http://www.w3.org/2000/svg" height="16px" viewBox="0 0 24 24" width="16px" fill="#e3e3e3"><path d="M0 0h24v24H0zm0 0h24v24H0zm0 0h24v24H0V0zm0 0h24v24H0V0z" fill="none"/><path d="M21 21.78L4.22 5 3 6.22l2.04 2.04C4.42 8.6 4 9.25 4 10v10c0 1.1.9 2 2 2h12c.23 0 .45-.05.66-.12L19.78 23 21 21.78zM8.9 6c0-1.71 1.39-3.1 3.1-3.1s3.1 1.39 3.1 3.1v2H9.66L20 18.34V10c0-1.1-.9-2-2-2h-1V6c0-2.76-2.24-5-5-5-2.56 0-4.64 1.93-4.94 4.4L8.9 7.24V6z"/></svg> unshackle
    <br/>
    <sup><em>Movie, TV, and Music Archival Software</em></sup>
</p>

## What is unshackle?

unshackle is a fork of [Devine](https://github.com/devine-dl/devine/), a powerful archival tool for downloading movies, TV shows, and music from streaming services. Built with a focus on modularity and extensibility, it provides a robust framework for content acquisition with support for DRM-protected content.

## Key Features

- 🚀 **Easy Installation** - Simple UV installation
- 🎥 **Multi-Media Support** - Movies, TV episodes, and music
- 🛠️ **Built-in Parsers** - DASH/HLS and ISM manifest support
- 🔒 **DRM Support** - Widevine and PlayReady integration
- 💾 **Flexible Storage** - Local and remote key vaults
- 👥 **Multi-Profile Auth** - Support for cookies and credentials
- 🤖 **Smart Naming** - Automatic P2P-style filename structure
- ⚙️ **Configurable** - YAML-based configuration
- ❤️ **Open Source** - Fully open-source with community contributions welcome

## Quick Start

### Installation

This installs the latest version directly from the GitHub repository:

```shell
git clone https://github.com/unshackle-dl/unshackle.git
cd unshackle
uv sync
uv run unshackle --help
```

### Install unshackle as a global (per-user) tool

```bash
uv tool install git+https://github.com/unshackle-dl/unshackle.git
# Then run:
uvx unshackle --help   # or just `unshackle` once PATH updated
```

> [!NOTE]
> After installation, you may need to add the installation path to your PATH environment variable if prompted.
>
> **Recommended:** Use `uv run unshackle` instead of direct command execution to ensure proper virtual environment activation.

### Basic Usage

```shell
# Check available commands
uv run unshackle --help

# Configure your settings
uv run unshackle cfg --help

# Confirm setup and all dependencies exist
uv run automaterr env check

# Download content (requires configured services)
uv run unshackle dl SERVICE_NAME CONTENT_ID
```

## Documentation

For comprehensive setup guides, configuration options, and advanced usage:

📖 **[Visit our WIKI](https://github.com/unshackle-dl/unshackle/wiki)**

The WIKI contains detailed information on:

- Service configuration
- DRM configuration
- Advanced features and troubleshooting

For guidance on creating services, see our [WIKI documentation](https://github.com/unshackle-dl/unshackle/wiki).

## End User License Agreement

unshackle and it's community pages should be treated with the same kindness as other projects.
Please refrain from spam or asking for questions that infringe upon a Service's End User License Agreement.

1. Do not use unshackle for any purposes of which you do not have the rights to do so.
2. Do not share or request infringing content; this includes widevine Provision Keys, Content Encryption Keys,
   or Service API Calls or Code.
3. The Core codebase is meant to stay Free and Open-Source while the Service code should be kept private.
4. Do not sell any part of this project, neither alone nor as part of a bundle.
   If you paid for this software or received it as part of a bundle following payment, you should demand your money
   back immediately.
5. Be kind to one another and do not single anyone out.

## Licensing

This software is licensed under the terms of [GNU General Public License, Version 3.0](LICENSE).  
You can find a copy of the license in the LICENSE file in the root folder.

---

[Export Cookies]: https://addons.mozilla.org/addon/export-cookies-txt
[Open Cookies.txt]: https://chrome.google.com/webstore/detail/gdocmgbfkjnnpapoeobnolbbkoibbcif
