#!/bin/bash
#
# MAT2 Nautilus Extension Uninstaller
# Removes the metadata cleaning extension from Nautilus
#

set -e

EXTENSION_FILE="mat2-nautilus-extension.py"
EXTENSIONS_DIR="$HOME/.local/share/nautilus-python/extensions"
INSTALLED_FILE="$EXTENSIONS_DIR/$EXTENSION_FILE"

echo "========================================="
echo "MAT2 Nautilus Extension Uninstaller"
echo "========================================="
echo

# Check if extension is installed
if [ ! -f "$INSTALLED_FILE" ]; then
    echo "Extension is not installed."
    echo "Location checked: $INSTALLED_FILE"
    exit 0
fi

# Remove extension
echo "Removing extension..."
rm -f "$INSTALLED_FILE"
echo "  Removed: $INSTALLED_FILE"
echo

# Success message
echo "========================================="
echo "Uninstallation complete!"
echo "========================================="
echo ""
echo "To complete the removal, restart Nautilus:"
echo ""
echo "    nautilus -q"
echo ""
echo "The extension has been removed. Your mat2"
echo "installation is not affected."
echo ""
