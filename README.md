# OfflinePackMaster

A Python utility for downloading npm packages and all their dependencies recursively for offline use.

## Overview

OfflinePackMaster allows you to download npm packages along with their entire dependency tree as `.tgz` files. This is particularly useful for:

- Setting up development environments in air-gapped or offline systems
- Creating local package caches
- Ensuring reproducible builds with exact package versions
- Preparing packages for environments with limited or no internet access

## Features

- 📦 Downloads npm packages with all dependencies recursively
- 🔍 Resolves version ranges (^, ~, *, etc.) to exact versions
- 🪟 Cross-platform support (Windows, macOS, Linux)
- 📝 Tracks failed downloads in a log file
- 🎯 Supports scoped packages (e.g., `@types/node`)
- ⚡ Avoids duplicate downloads

## Prerequisites

- Python 3.6 or higher
- Node.js and npm installed and accessible from the command line

## Installation

### Option 1: Download from Releases

You can download the latest release directly from the [Releases page](https://github.com/ori-halevi/OfflinePackMaster/releases).

### Option 2: Clone from Source

```bash
git clone https://github.com/ori-halevi/OfflinePackMaster.git
cd OfflinePackMaster
```

## Usage

1. Run the script:
```bash
python offlinepackmaster.py
```

2. Enter the package name when prompted. You can specify a version or use version ranges:
```
express
express@5.1.0
express@^4.0.0
@types/node@20.10.0
```

3. The script will:
   - Download the specified package
   - Extract and read its `package.json`
   - Recursively download all dependencies
   - Save all `.tgz` files in the `put-pacs-here` directory

4. All downloaded packages will be saved as `.tgz` files in the `put-pacs-here` folder

## Output

- **Downloaded packages**: All `.tgz` files are stored in the `put-pacs-here` directory
- **Failed downloads**: Any packages that fail to download are logged in `put-pacs-here/failed_packages.log`

## Example

```
Enter the package you want to download (with optional version, e.g., express@5.1.0):
> express@4.18.0

[INFO] Downloading express@4.18.0
[INFO] Downloading accepts@1.3.8
[INFO] Downloading mime-types@2.1.35
[INFO] Downloading mime-db@1.52.0
...

All packages downloaded successfully!
```

## Version Resolution

The tool automatically handles version ranges:
- `^1.2.3` - Compatible with version
- `~1.2.3` - Approximately equivalent to version
- `*` or `latest` - Latest version
- `>`, `<`, `>=`, `<=` - Comparison operators

## Troubleshooting

### npm not found
Ensure Node.js is installed and npm is in your system's PATH.

### Package download fails
Check the `failed_packages.log` file in the `put-pacs-here` directory for details on failed downloads.

### Permission errors
Make sure you have write permissions in the directory where you're running the script.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Repository

https://github.com/ori-halevi/OfflinePackMaster
