#!/bin/bash
#
# MAT2 Nautilus Extension Installer
# Installs the metadata cleaning extension for Nautilus
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_FILE="mat2-nautilus-extension.py"
EXTENSIONS_DIR="$HOME/.local/share/nautilus-python/extensions"

echo "========================================="
echo "MAT2 Nautilus Extension Installer"
echo "========================================="
echo

# Check if mat2 is installed
echo "Checking dependencies..."

if ! command -v mat2 &> /dev/null; then
    echo "ERROR: mat2 is not installed."
    echo ""
    echo "Install it with:"
    echo "    sudo apt install mat2"
    echo ""
    exit 1
fi

MAT2_VERSION=$(mat2 --version 2>&1 | head -n1)
echo "  mat2: $MAT2_VERSION"

# Check if python3-nautilus is installed
if ! python3 -c "from gi.repository import Nautilus" 2>/dev/null; then
    echo "WARNING: python3-nautilus may not be installed."
    echo ""
    echo "Install it with:"
    echo "    sudo apt install python3-nautilus"
    echo ""
fi

# Check if extension file exists
if [ ! -f "$SCRIPT_DIR/$EXTENSION_FILE" ]; then
    echo "ERROR: Extension file not found: $SCRIPT_DIR/$EXTENSION_FILE"
    exit 1
fi

echo "  Extension file: Found"
echo

# Create extensions directory
echo "Creating extensions directory..."
mkdir -p "$EXTENSIONS_DIR"
echo "  Created: $EXTENSIONS_DIR"

# Copy extension file
echo "Installing extension..."
cp "$SCRIPT_DIR/$EXTENSION_FILE" "$EXTENSIONS_DIR/"
chmod +x "$EXTENSIONS_DIR/$EXTENSION_FILE"
echo "  Installed: $EXTENSIONS_DIR/$EXTENSION_FILE"
echo

# Success message
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "To activate the extension, restart Nautilus:"
echo ""
echo "    nautilus -q"
echo ""
echo "Then right-click on any supported file to see"
echo "the 'Clean Metadata' option."
echo ""
echo "Supported formats: PDF, images, audio, video,"
echo "office documents, archives, and more."
echo ""
echo "Run 'mat2 --list' to see all supported formats."
echo ""
