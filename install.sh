#!/bin/bash
#
# MAT2 Nautilus Extension Installer
# Installs the metadata cleaning extension for Nautilus
# Automatically installs required dependencies
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_FILE="mat2-nautilus-extension.py"
EXTENSIONS_DIR="$HOME/.local/share/nautilus-python/extensions"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "MAT2 Nautilus Extension Installer"
echo "========================================="
echo
echo -e "${YELLOW}Note: This script may ask for your sudo password${NC}"
echo -e "${YELLOW}      to install missing dependencies.${NC}"
echo

# Track what was installed
INSTALLED_PACKAGES=()

#
# Function to install a package
#
install_package() {
    local package=$1
    echo -e "  Installing ${YELLOW}$package${NC}..."
    if sudo apt install -y "$package" > /dev/null 2>&1; then
        INSTALLED_PACKAGES+=("$package")
        echo -e "  ${GREEN}Installed: $package${NC}"
        return 0
    else
        echo -e "  ${RED}Failed to install: $package${NC}"
        return 1
    fi
}

#
# Check and install required dependencies
#
echo "Checking dependencies..."
echo

# --- mat2 (required) ---
echo "  [1/4] mat2 (metadata cleaner)..."
if command -v mat2 &> /dev/null; then
    MAT2_VERSION=$(mat2 --version 2>&1 | head -n1)
    echo -e "        ${GREEN}Found: $MAT2_VERSION${NC}"
else
    echo -e "        ${YELLOW}Not found. Installing...${NC}"
    if ! install_package "mat2"; then
        echo
        echo -e "${RED}ERROR: Failed to install mat2.${NC}"
        echo "Please install it manually: sudo apt install mat2"
        exit 1
    fi
    # Verify installation
    if ! command -v mat2 &> /dev/null; then
        echo -e "${RED}ERROR: mat2 installation failed.${NC}"
        exit 1
    fi
    MAT2_VERSION=$(mat2 --version 2>&1 | head -n1)
    echo -e "        ${GREEN}Installed: $MAT2_VERSION${NC}"
fi

# --- python3-nautilus (required) ---
echo "  [2/4] python3-nautilus (Nautilus extensions)..."
if python3 -c "from gi.repository import Nautilus" 2>/dev/null; then
    echo -e "        ${GREEN}Found${NC}"
else
    echo -e "        ${YELLOW}Not found. Installing...${NC}"
    if ! install_package "python3-nautilus"; then
        echo
        echo -e "${RED}ERROR: Failed to install python3-nautilus.${NC}"
        echo "Please install it manually: sudo apt install python3-nautilus"
        exit 1
    fi
    # Verify installation
    if ! python3 -c "from gi.repository import Nautilus" 2>/dev/null; then
        echo -e "${RED}ERROR: python3-nautilus installation failed or Nautilus GIR not available.${NC}"
        echo "Try: sudo apt install gir1.2-nautilus-4.0 or gir1.2-nautilus-3.0"
        exit 1
    fi
    echo -e "        ${GREEN}Installed${NC}"
fi

# --- libnotify-bin (recommended) ---
echo "  [3/4] libnotify-bin (notifications)..."
if command -v notify-send &> /dev/null; then
    echo -e "        ${GREEN}Found${NC}"
else
    echo -e "        ${YELLOW}Not found. Installing...${NC}"
    if install_package "libnotify-bin"; then
        echo -e "        ${GREEN}Installed${NC}"
    else
        echo -e "        ${YELLOW}WARNING: Could not install libnotify-bin.${NC}"
        echo -e "        ${YELLOW}         Notifications will not work.${NC}"
    fi
fi

# --- zenity (recommended) ---
echo "  [4/4] zenity (error dialogs)..."
if command -v zenity &> /dev/null; then
    echo -e "        ${GREEN}Found${NC}"
else
    echo -e "        ${YELLOW}Not found. Installing...${NC}"
    if install_package "zenity"; then
        echo -e "        ${GREEN}Installed${NC}"
    else
        echo -e "        ${YELLOW}WARNING: Could not install zenity.${NC}"
        echo -e "        ${YELLOW}         Error dialogs will fallback to logs.${NC}"
    fi
fi

echo

# Show summary of installed packages
if [ ${#INSTALLED_PACKAGES[@]} -gt 0 ]; then
    echo -e "${GREEN}Installed packages:${NC} ${INSTALLED_PACKAGES[*]}"
    echo
fi

# Check if extension file exists
if [ ! -f "$SCRIPT_DIR/$EXTENSION_FILE" ]; then
    echo -e "${RED}ERROR: Extension file not found: $SCRIPT_DIR/$EXTENSION_FILE${NC}"
    exit 1
fi

echo "Extension file: Found"
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
echo -e "${GREEN}Installation complete!${NC}"
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
