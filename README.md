<p align="center">
    <img width="16" height="16" alt="no_encryption" src="https://github.com/user-attachments/assets/6ff88473-0dd2-4bbc-b1ea-c683d5d7a134" /> unshackle
    <br/>
    <sup><em>Movie, TV, and Music Archival Software</em></sup>
    <br/>
</p>

## What is unshackle?

unshackle is a fork of [Devine](https://github.com/devine-dl/devine/), a powerful archival tool for downloading movies, TV shows, and music from streaming services. Built with a focus on modularity and extensibility, it provides a robust framework for content acquisition with support for DRM-protected content.

## Included services (from my fork)
- Netflix (video not currently working. audio, subtitles and chapters are fine)
- Will add more soon

## Key Features

- 🚀 **Easy Installation** - Simple UV installation
- 🎥 **Multi-Media Support** - Movies, TV episodes, and music
- 🛠️ **Built-in Parsers** - DASH/HLS and ISM manifest support
- 🔒 **DRM Support** - Widevine and PlayReady integration
- 🌈 **HDR10+DV Hybrid** - Hybrid Dolby Vision injection via [dovi_tool](https://github.com/quietvoid/dovi_tool)
- 💾 **Flexible Storage** - Local and remote key vaults
- 👥 **Multi-Profile Auth** - Support for cookies and credentials
- 🤖 **Smart Naming** - Automatic P2P-style filename structure
- ⚙️ **Configurable** - YAML-based configuration
- ❤️ **Open Source** - Fully open-source with community contributions welcome

## Quick Start

### Install unshackle as a global (per-user) tool (recommended)

```bash
uv tool install git+https://github.com/windigerbus/unshackle.git
# Then run:
uvx unshackle --help   # or just `unshackle` once PATH updated
```

### Installation

This installs the latest version directly from the GitHub repository:

```shell
git clone https://github.com/windigerbus/unshackle.git
cd unshackle
uv sync
uv run unshackle --help
```

> [!NOTE]
> After installation, you may need to add the installation path to your PATH environment variable if prompted.

### Basic Usage

```shell
# Check available commands
unshackle --help

# Download content (requires configured services)
unshackle dl SERVICE_NAME CONTENT_ID
```

## Documentation

For comprehensive setup guides, configuration options, and advanced usage:

📖 **[Visit the WIKI](https://github.com/unshackle-dl/unshackle/wiki)**

The WIKI contains detailed information on:

- Service configuration
- DRM configuration
- Advanced features and troubleshooting

## Licensing

This software is licensed under the terms of [GNU General Public License, Version 3.0](LICENSE).  
You can find a copy of the license in the LICENSE file in the root folder.
