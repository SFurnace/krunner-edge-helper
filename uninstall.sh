#!/bin/bash
# Uninstallation script for Edge Bookmarks KRunner Plugin

set -e

PLUGIN_DIR="$HOME/.local/share/krunner/dbusplugins"
DESKTOP_DIR="$HOME/.local/share/kservices5"

echo "=== Edge Bookmarks KRunner Plugin Uninstallation ==="
echo

# Remove plugin files
echo "Removing plugin files..."
rm -f "$PLUGIN_DIR/edge_bookmarks_runner.py"
rm -f "$PLUGIN_DIR/bookmark_parser.py"
rm -f "$PLUGIN_DIR/search_engine.py"
rm -f "$PLUGIN_DIR/pinyin_matcher.py"
rm -f "$PLUGIN_DIR/config.py"

# Remove Python cache
rm -rf "$PLUGIN_DIR/__pycache__"

echo "✓ Plugin files removed"

# Remove desktop file
echo "Removing desktop file..."
rm -f "$DESKTOP_DIR/plasma-runner-edge-bookmarks.desktop"

echo "✓ Desktop file removed"

# Restart KRunner
echo
echo "Restarting KRunner..."
killall krunner 2>/dev/null || true
kquitapp5 krunner 2>/dev/null || true

echo
echo "=== Uninstallation Complete ==="
echo
echo "The plugin has been removed."
echo "Python dependencies (pypinyin, rapidfuzz, etc.) were NOT removed."
echo "To remove them manually, run:"
echo "  pip3 uninstall pypinyin rapidfuzz dbus-python PyQt5"
echo
