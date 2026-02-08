#!/bin/bash
# Installation script for KRunner Edge Helper

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation directories
PLUGIN_DIR="$HOME/.local/share/krunner/dbusplugins/krunner-edge-helper"
DBUS_SERVICE_DIR="$HOME/.local/share/dbus-1/services"
DBUSPLUGINS_DIR="$HOME/.local/share/krunner/dbusplugins"

echo "=== KRunner Edge Helper Installation ==="
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

# Stop any running instances FIRST
echo
echo "Stopping any running instances..."
RUNNING_PIDS=$(ps aux | grep "krunner_edge_helper.py" | grep -v grep | awk '{print $2}')
if [ -n "$RUNNING_PIDS" ]; then
    for pid in $RUNNING_PIDS; do
        kill $pid 2>/dev/null && echo "  Killed process $pid"
    done
    sleep 2
else
    echo "  No running instances found"
fi

# Clean old installation and caches
echo
echo "Cleaning old installation and caches..."
rm -rf "$PLUGIN_DIR"
echo "  ✓ Old installation cleaned"

# Install Python dependencies
echo
echo "Installing Python dependencies..."
pip3 install --user -r "$SCRIPT_DIR/requirements.txt"

echo "✓ Dependencies installed"

# Create directories
mkdir -p "$PLUGIN_DIR"
mkdir -p "$DBUS_SERVICE_DIR"
mkdir -p "$DBUSPLUGINS_DIR"

echo "✓ Directories created"

# Copy plugin files to subdirectory
echo
echo "Installing plugin files..."

# Copy all source files
cp "$SCRIPT_DIR/src/krunner_edge_helper.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/src/bookmark_parser.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/src/search_engine.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/src/pinyin_matcher.py" "$PLUGIN_DIR/"
cp "$SCRIPT_DIR/src/config.py" "$PLUGIN_DIR/"

# Make main script executable
chmod +x "$PLUGIN_DIR/krunner_edge_helper.py"

echo "✓ Plugin files installed to $PLUGIN_DIR"

# Install DBus service file
sed "s|USER_HOME_PLACEHOLDER|$HOME|g" "$SCRIPT_DIR/service/org.kde.krunner.edgehelper.service" \
    > "$DBUS_SERVICE_DIR/org.kde.krunner.edgehelper.service"

echo "✓ DBus service file installed to $DBUS_SERVICE_DIR"

# Install desktop file to dbusplugins root (KDE 6 requirement)
cp "$SCRIPT_DIR/service/krunner-edge-helper.desktop" "$DBUSPLUGINS_DIR/"

echo "✓ Desktop file installed to $DBUSPLUGINS_DIR"

# Restart KRunner
echo
echo "Restarting KRunner..."
killall krunner 2>/dev/null || true
kquitapp5 krunner 2>/dev/null || kquitapp6 krunner 2>/dev/null || true
sleep 2

# Start the plugin
echo
echo "Starting plugin..."
python3 "$PLUGIN_DIR/krunner_edge_helper.py" > /tmp/krunner_edge_helper.log 2>&1 &
PLUGIN_PID=$!
sleep 2

# Verify installation
if ps -p $PLUGIN_PID > /dev/null 2>&1; then
    echo "✓ Plugin started successfully (PID: $PLUGIN_PID)"
else
    echo "✗ Plugin failed to start"
    echo "Check logs: cat /tmp/krunner_edge_helper.log"
    exit 1
fi

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
echo "  - Check logs: cat /tmp/krunner_edge_helper.log"
echo "  - Manual start: python3 $PLUGIN_DIR/krunner_edge_helper.py"
echo "  - Restart KRunner: kquitapp5 krunner"
echo "  - Use restart script: $SCRIPT_DIR/restart_plugin.sh"
echo
