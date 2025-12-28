# MAT2 Nautilus Extension

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Nautilus](https://img.shields.io/badge/Nautilus-3.0%20%7C%204.x-green.svg)](https://apps.gnome.org/Nautilus/)

A Nautilus file manager extension that adds a **"Clean Metadata"** option to the right-click context menu, using [mat2](https://0xacab.org/jvoisin/mat2) (Metadata Anonymisation Toolkit 2) to remove metadata from files.

## Features

- **Right-click integration**: Adds "Clean Metadata" to the context menu
- **Multiple file support**: Clean metadata from multiple files at once
- **40+ formats supported**: Images, documents, audio, video, archives, and more
- **Safe operation**: Creates cleaned copies (`file.cleaned.ext`), preserves originals
- **System notifications**: Non-intrusive feedback on cleaning results
- **Security hardened**: Path validation, timeout protection, no shell injection

## Compatibility

| Distribution | Nautilus Version | Status |
|--------------|------------------|--------|
| Debian 13 (Trixie) | 49.x | Tested |
| Ubuntu 24.04+ | 46.x+ | Compatible |
| Fedora 40+ | 46.x+ | Compatible |
| Arch Linux | Latest | Compatible |

Supports Nautilus 3.0, 4.0, and 4.1 APIs with automatic detection.

## Requirements

- **Nautilus** file manager (GNOME Files)
- **mat2**: Metadata Anonymisation Toolkit 2
- **python3-nautilus**: Python bindings for Nautilus extensions
- **libnotify** (optional): For desktop notifications
- **zenity** (optional): For error dialogs

### Installing Dependencies

**Debian/Ubuntu:**
```bash
sudo apt install mat2 python3-nautilus libnotify-bin zenity
```

**Fedora:**
```bash
sudo dnf install mat2 nautilus-python libnotify zenity
```

**Arch Linux:**
```bash
sudo pacman -S mat2 python-nautilus libnotify zenity
```

## Installation

### From GitHub

```bash
# Clone the repository
git clone https://github.com/vdiriern/nautilus-mat2-extension.git
cd nautilus-mat2-extension

# Run the installation script
./install.sh

# Restart Nautilus
nautilus -q
```

### Manual Installation

```bash
# Create the extensions directory if it doesn't exist
mkdir -p ~/.local/share/nautilus-python/extensions/

# Copy the extension
cp mat2-nautilus-extension.py ~/.local/share/nautilus-python/extensions/

# Restart Nautilus
nautilus -q
```

## Uninstallation

### Automatic

```bash
cd nautilus-mat2-extension
./uninstall.sh
nautilus -q
```

### Manual

```bash
rm ~/.local/share/nautilus-python/extensions/mat2-nautilus-extension.py
nautilus -q
```

## Usage

1. Right-click on one or more files in Nautilus
2. Select **"Clean Metadata"** from the context menu
3. Wait for the notification showing the results
4. Find the cleaned files with `.cleaned` suffix in the same directory

### Example

```
photo.jpg          →  photo.cleaned.jpg
document.pdf       →  document.cleaned.pdf
recording.mp3      →  recording.cleaned.mp3
```

## Supported File Formats

mat2 supports metadata removal from 40+ file formats:

| Category | Formats |
|----------|---------|
| **Images** | JPEG, PNG, GIF, BMP, TIFF, WebP, HEIC, SVG |
| **Documents** | PDF, ODT, ODS, ODP, DOCX, XLSX, PPTX, EPUB |
| **Audio** | MP3, FLAC, OGG, Opus, WAV, AIFF |
| **Video** | MP4, AVI, WMV |
| **Archives** | ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ |
| **Web** | HTML, CSS |

For the complete list, run:
```bash
mat2 --list
```

## Troubleshooting

### Menu option doesn't appear

1. Verify mat2 is installed: `mat2 --version`
2. Verify python3-nautilus is installed: `dpkg -l python3-nautilus`
3. Check the extension is in the correct location:
   ```bash
   ls ~/.local/share/nautilus-python/extensions/mat2-nautilus-extension.py
   ```
4. Restart Nautilus: `nautilus -q`
5. Check for errors: `NAUTILUS_PYTHON_DEBUG=misc nautilus`

### "mat2 not installed" error

Install mat2 using your package manager (see [Installing Dependencies](#installing-dependencies)).

### Cleaning fails for some files

- Check file permissions (need read access to original)
- Check directory permissions (need write access for cleaned file)
- Some files may have unsupported or corrupted metadata

### Extension crashes Nautilus

Check the logs:
```bash
journalctl --user -b | grep nautilus
```

## How It Works

1. When you right-click on files, the extension checks if they are supported by mat2
2. Only supported files show the "Clean Metadata" menu option
3. When clicked, mat2 processes each file and creates a cleaned copy
4. The original files are preserved (not modified)
5. A system notification shows the results

## Security

This extension was developed with security in mind:

- **Path validation**: Prevents path traversal attacks
- **System directory protection**: Won't process files in `/bin`, `/usr`, `/etc`, etc.
- **Timeout protection**: 5-minute timeout per file to prevent hangs
- **No shell injection**: Uses subprocess with argument lists, not shell commands
- **No eval/exec**: No dynamic code execution

Scanned with Semgrep security rules (OWASP, bandit, command-injection) - no vulnerabilities found.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- [mat2](https://0xacab.org/jvoisin/mat2) - The Metadata Anonymisation Toolkit 2
- [nautilus-python](https://gitlab.gnome.org/GNOME/nautilus-python) - Python bindings for Nautilus

## Author

**Homero Thompson del Lago del Terror** - [GitHub](https://github.com/vdirienzo)
