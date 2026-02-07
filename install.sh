#!/bin/bash
# Installation script for Edge Bookmarks KRunner Plugin

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="edge_bookmarks_runner.py"
DESKTOP_FILE="plasma-runner-edge-bookmarks.desktop"

# Installation directories
PLUGIN_DIR="$HOME/.local/share/krunner/dbusplugins"
DBUS_SERVICE_DIR="$HOME/.local/share/dbus-1/services"

echo "=== Edge Bookmarks KRunner Plugin Installation ==="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    echo "Install with: sudo dnf install python3-pip  # For Fedora/RHEL"
    echo "          or: sudo apt install python3-pip  # For Debian/Ubuntu"
    exit 1
fi

echo "✓ pip3 found"

# Install Python dependencies
echo
echo "Installing Python dependencies..."
pip3 install --user -r "$SCRIPT_DIR/requirements.txt"

echo "✓ Dependencies installed"

# Create directories if they don't exist
mkdir -p "$PLUGIN_DIR"
mkdir -p "$DBUS_SERVICE_DIR"

echo "✓ Directories created"

# Copy plugin files
echo
echo "Installing plugin files..."

# Copy main plugin
cp "$SCRIPT_DIR/$PLUGIN_NAME" "$PLUGIN_DIR/"
chmod +x "$PLUGIN_DIR/$PLUGIN_NAME"

# Copy supporting modules
cp "$SCRIPT_DIR/bookmark_parser.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/search_engine.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/pinyin_matcher.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/config.py" "$PLUGIN_DIR/"

# Copy desktop file to plugin directory (KDE 6)
cp "$SCRIPT_DIR/$DESKTOP_FILE" "$PLUGIN_DIR/"

# Copy DBus service file (create it from template)
cat > "$DBUS_SERVICE_DIR/org.kde.plasma.runner.edgebookmarks.service" << EOF
[D-BUS Service]
Name=org.kde.plasma.runner.edgebookmarks
Exec=$PLUGIN_DIR/$PLUGIN_NAME
EOF

echo "✓ Plugin files installed to $PLUGIN_DIR"
echo "✓ Desktop file installed to $PLUGIN_DIR"
echo "✓ DBus service file installed to $DBUS_SERVICE_DIR"

# Restart KRunner
echo
echo "Restarting KRunner..."
killall krunner 2>/dev/null || true
kquitapp5 krunner 2>/dev/null || true
sleep 2

echo
echo "=== Installation Complete ==="
echo
echo "Usage:"
echo "  1. Press Alt+Space (or Alt+F2) to open KRunner"
echo "  2. Type 'b' followed by your search query"
echo "  3. Example: 'b github' or 'b 中国' or 'b zg'"
echo
echo "Configuration:"
echo "  Edit $PLUGIN_DIR/config.py to customize:"
echo "  - Bookmark file path"
echo "  - Trigger keyword"
echo "  - Search settings"
echo
echo "Troubleshooting:"
echo "  - Check logs: journalctl --user -f | grep edge_bookmarks"
echo "  - Manual start: python3 $PLUGIN_DIR/$PLUGIN_NAME"
echo "  - Restart KRunner: kquitapp5 krunner"
echo
