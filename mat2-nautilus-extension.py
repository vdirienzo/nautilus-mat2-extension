#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAT2 Metadata Cleaning Extension for Nautilus
==============================================
Nautilus extension for removing metadata from files using mat2
(Metadata Anonymisation Toolkit 2).

Features:
- Clean metadata from individual files
- Clean metadata from multiple files at once
- Support for 40+ file formats (images, documents, audio, video, etc.)
- Creates cleaned copies (preserves originals)
- System notifications for feedback

Author: Homero Thompson del Lago del Terror
Date: December 2025
License: MIT
"""

import logging
import os
import subprocess
from typing import List, Optional
from urllib.parse import unquote, urlparse

# Configure logging for the extension
logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s: %(levelname)s: %(message)s'
)
logger = logging.getLogger('mat2-nautilus')

# Detect available Nautilus version
# IMPORTANT: DO NOT use exit() - it crashes Nautilus
from gi import require_version

NAUTILUS_VERSION = None
_import_error = None

# Try Nautilus 4.1 (Debian 13/Trixie, Ubuntu 24.04+)
try:
    require_version('Nautilus', '4.1')
    from gi.repository import Nautilus, GObject, GLib
    NAUTILUS_VERSION = 4
except (ValueError, ImportError):
    pass

# Try Nautilus 4.0 (older versions)
if NAUTILUS_VERSION is None:
    try:
        require_version('Nautilus', '4.0')
        from gi.repository import Nautilus, GObject, GLib
        NAUTILUS_VERSION = 4
    except (ValueError, ImportError):
        pass

# Try Nautilus 3.0 (legacy)
if NAUTILUS_VERSION is None:
    try:
        require_version('Nautilus', '3.0')
        from gi.repository import Nautilus, GObject, GLib
        NAUTILUS_VERSION = 3
    except (ValueError, ImportError) as e:
        _import_error = e

# If no version could be imported, create dummy class to avoid crash
if NAUTILUS_VERSION is None:
    logger.error(f"Could not import Nautilus: {_import_error}")
    logger.error("Extension will not be available.")

    # Create dummy classes so the file loads without error
    class GObject:
        class GObject:
            pass

    class Nautilus:
        class MenuProvider:
            pass

        class MenuItem:
            def __init__(self, **kwargs):
                pass

            def connect(self, *args):
                pass

    class GLib:
        @staticmethod
        def timeout_add(delay, callback, *args):
            pass


# File extensions commonly supported by mat2
# Used for quick pre-filtering before expensive libmat2 check
SUPPORTED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.heic', '.ppm', '.svg', '.svgz',
    # Documents
    '.pdf', '.odt', '.ods', '.odp', '.odg', '.odf', '.odi', '.odc',
    '.docx', '.xlsx', '.pptx', '.epub', '.ncx',
    # Audio
    '.mp3', '.mp1', '.mp2', '.mpga', '.mpega', '.flac', '.ogg', '.oga',
    '.opus', '.spx', '.wav', '.aif', '.aiff', '.aifc',
    # Video
    '.mp4', '.mpg4', '.m4v', '.avi', '.wmv',
    # Archives
    '.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.torrent',
    # Web
    '.html', '.htm', '.shtml', '.xhtml', '.xht', '.css',
    # Text
    '.txt', '.text',
}


class Mat2CleanerExtension(GObject.GObject, Nautilus.MenuProvider):
    """Nautilus extension for cleaning file metadata with mat2."""

    def __init__(self) -> None:
        """Initialize the extension."""
        super().__init__()
        self._mat2_checked: bool = False
        self._mat2_available: Optional[bool] = None

    def check_mat2_available(self) -> bool:
        """Check if mat2 is installed (lazy check, once per session).

        Returns:
            True if mat2 is available, False otherwise
        """
        if self._mat2_checked:
            return self._mat2_available

        self._mat2_checked = True
        try:
            result = subprocess.run(
                ['mat2', '--version'],
                capture_output=True,
                timeout=2
            )
            self._mat2_available = result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self._mat2_available = False

        if not self._mat2_available:
            logger.error("mat2 is not installed or not accessible")

        return self._mat2_available

    def validate_path(self, path: str) -> bool:
        """Validate that a path is safe (no traversal attacks).

        Args:
            path: The path to validate

        Returns:
            True if the path is safe, False otherwise
        """
        # Must be absolute path
        if not os.path.isabs(path):
            logger.warning(f"Path validation failed: not absolute: {path}")
            return False

        # Resolve the path to catch symlink attacks
        try:
            resolved = os.path.realpath(path)
        except (OSError, ValueError) as e:
            logger.warning(f"Path validation failed: cannot resolve: {e}")
            return False

        # Check for path traversal (.. components after resolution)
        if '..' in resolved.split(os.sep):
            logger.warning(f"Path validation failed: traversal detected: {path}")
            return False

        # Don't allow operations on critical system directories
        dangerous_prefixes = ['/bin', '/sbin', '/usr', '/etc', '/var', '/boot', '/root']
        for prefix in dangerous_prefixes:
            if resolved.startswith(prefix + os.sep) or resolved == prefix:
                logger.warning(f"Path validation failed: system directory: {resolved}")
                return False

        return True

    def is_file_supported(self, path: str) -> bool:
        """Check if a file is supported by mat2.

        Uses quick extension check first, then validates with libmat2 if needed.

        Args:
            path: Path to the file

        Returns:
            True if the file is supported by mat2
        """
        # Quick filter by extension
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            return False

        # For better accuracy, validate with libmat2
        try:
            from libmat2 import parser_factory
            parser, _ = parser_factory.get_parser(path)
            return parser is not None
        except (ImportError, ValueError, Exception) as e:
            # If libmat2 is not available or file is invalid,
            # fall back to extension-based check (already passed)
            logger.debug(f"libmat2 check failed for {path}: {e}")
            return True  # Extension matched, assume supported

    def get_path_from_uri(self, uri: str) -> Optional[str]:
        """Convert a file URI to a system path.

        Args:
            uri: File URI (e.g., file:///home/user/file.pdf)

        Returns:
            System path or None if conversion fails
        """
        try:
            parsed = urlparse(uri)
            if parsed.scheme != 'file':
                return None
            path = unquote(parsed.path)
            return path
        except (ValueError, TypeError) as e:
            logger.warning(f"URI parsing error: {e}")
            return None

    def get_file_items(self, *args) -> List:
        """Entry point for context menu items.

        Called by Nautilus when user right-clicks on files.

        Args:
            *args: Nautilus 3 passes (window, files), Nautilus 4 passes (files)

        Returns:
            List of menu items to display
        """
        # If Nautilus was not imported correctly, don't show menu
        if NAUTILUS_VERSION is None:
            return []

        # Verify mat2 is available (lazy check)
        if not self.check_mat2_available():
            # Show error only once per session
            if not hasattr(self, '_error_shown'):
                self._error_shown = True
                self.show_error(
                    "mat2 not installed",
                    "Install mat2 to use this extension:\n\n"
                    "sudo apt install mat2"
                )
            return []

        # Compatibility between Nautilus 3 and 4
        if len(args) == 1:  # Nautilus 4
            files = args[0]
        else:  # Nautilus 3
            files = args[1]

        if not files:
            return []

        # Convert URIs to paths and filter
        paths = []
        for file_info in files:
            if hasattr(file_info, 'get_uri'):
                uri = file_info.get_uri()
                path = self.get_path_from_uri(uri)

                # Only include valid, supported files
                if (path and
                    os.path.isfile(path) and
                    self.validate_path(path) and
                    self.is_file_supported(path)):
                    paths.append(path)

        if not paths:
            return []

        # Create menu item
        return [self.create_menu_item(paths)]

    def get_background_items(self, *args) -> List:
        """Entry point for background context menu.

        Called when user right-clicks on empty space in a folder.
        We don't provide any options for this case.

        Returns:
            Empty list (no menu items for background click)
        """
        return []

    def create_menu_item(self, paths: List[str]) -> 'Nautilus.MenuItem':
        """Create the 'Clean Metadata' menu item.

        Args:
            paths: List of file paths to clean

        Returns:
            Nautilus menu item
        """
        if len(paths) == 1:
            label = "Clean Metadata"
            tip = "Remove metadata from this file using mat2"
        else:
            label = f"Clean Metadata ({len(paths)} files)"
            tip = f"Remove metadata from {len(paths)} files using mat2"

        item = Nautilus.MenuItem(
            name='Mat2Extension::CleanMetadata',
            label=label,
            tip=tip
        )
        item.connect('activate', self.on_clean_metadata, paths)
        return item

    def on_clean_metadata(self, menu: 'Nautilus.MenuItem', paths: List[str]) -> None:
        """Handler for the 'Clean Metadata' menu action.

        Delays execution to let the context menu close properly.

        Args:
            menu: The menu item that was clicked
            paths: List of file paths to clean
        """
        # Delay to let context menu close and transfer focus
        GLib.timeout_add(150, self._do_clean_metadata, paths)

    def _do_clean_metadata(self, paths: List[str]) -> bool:
        """Perform the actual metadata cleaning operation.

        Args:
            paths: List of file paths to clean

        Returns:
            False to prevent GLib.timeout_add from repeating
        """
        success_count = 0
        failed_count = 0
        unsupported_count = 0
        cleaned_files = []

        for path in paths:
            # Double-check path validation
            if not self.validate_path(path):
                logger.warning(f"Skipping invalid path: {path}")
                failed_count += 1
                continue

            if not os.path.isfile(path):
                logger.warning(f"Skipping non-file: {path}")
                failed_count += 1
                continue

            try:
                # Run mat2 (creates filename.cleaned.ext by default)
                result = subprocess.run(
                    ['mat2', '--unknown-members', 'omit', path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes max per file
                )

                if result.returncode == 0:
                    success_count += 1
                    # Determine the cleaned filename
                    base, ext = os.path.splitext(path)
                    cleaned_path = f"{base}.cleaned{ext}"
                    if os.path.exists(cleaned_path):
                        cleaned_files.append(os.path.basename(cleaned_path))
                    logger.info(f"Cleaned metadata: {path}")

                elif result.returncode == 1:
                    # Format not supported (not an error per mat2 design)
                    unsupported_count += 1
                    logger.info(f"Format not supported by mat2: {path}")

                else:
                    failed_count += 1
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    logger.error(f"mat2 failed on {path}: {error_msg}")

            except subprocess.TimeoutExpired:
                failed_count += 1
                logger.error(f"Timeout cleaning: {path}")

            except OSError as e:
                failed_count += 1
                logger.error(f"OS error cleaning {path}: {e}")

        # Show notification with results
        self._show_results(success_count, unsupported_count, failed_count, cleaned_files)

        return False  # Don't repeat GLib.timeout_add

    def _show_results(self, success: int, unsupported: int, failed: int,
                      cleaned_files: List[str]) -> None:
        """Show notification with cleaning results.

        Args:
            success: Number of successfully cleaned files
            unsupported: Number of unsupported format files
            failed: Number of failed files
            cleaned_files: List of cleaned file names
        """
        if success > 0 and failed == 0 and unsupported == 0:
            # All successful
            if success == 1 and cleaned_files:
                message = f"Created: {cleaned_files[0]}"
            else:
                message = f"{success} file(s) cleaned successfully"
            self.show_notification("Metadata Cleaned", message)

        elif success > 0:
            # Partial success
            parts = [f"{success} cleaned"]
            if unsupported > 0:
                parts.append(f"{unsupported} unsupported")
            if failed > 0:
                parts.append(f"{failed} failed")
            self.show_notification("Metadata Cleaning Complete", ", ".join(parts))

        elif unsupported > 0 and failed == 0:
            # All files were unsupported
            self.show_notification(
                "No Files Cleaned",
                f"{unsupported} file(s) not supported by mat2"
            )

        else:
            # All failed
            self.show_error(
                "Metadata Cleaning Failed",
                f"Could not clean {failed} file(s). Check file permissions."
            )

    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification.

        Args:
            title: Notification title
            message: Notification message
        """
        try:
            subprocess.run(
                ['notify-send', '-i', 'edit-clear-all', title, message],
                timeout=2,
                capture_output=True
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Silence notification errors - they are not critical
            logger.debug(f"Could not show notification: {title}")

    def show_error(self, title: str, message: str) -> None:
        """Show an error dialog using zenity.

        Args:
            title: Dialog title
            message: Error message
        """
        try:
            subprocess.run(
                ['zenity', '--error',
                 '--title', title,
                 '--text', message,
                 '--width', '400'],
                timeout=60,
                capture_output=True
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Fallback to logger if zenity is not available
            logger.error(f"Dialog error: {title} - {message}")
