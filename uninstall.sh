#!/bin/bash
# Uninstallation script for Edge Bookmarks KRunner Plugin

set -e

PLUGIN_DIR="$HOME/.local/share/krunner/dbusplugins"
DESKTOP_DIR="$HOME/.local/share/kservices5"
DBUS_SERVICE_DIR="$HOME/.local/share/dbus-1/services"

echo "=== Edge Bookmarks KRunner Plugin Uninstallation ==="
echo

# Step 1: Stop all running processes FIRST
echo "1. Stopping all running instances..."
RUNNING_PIDS=$(ps aux | grep "edge_bookmarks_runner.py" | grep -v grep | awk '{print $2}')
if [ -n "$RUNNING_PIDS" ]; then
    for pid in $RUNNING_PIDS; do
        kill $pid 2>/dev/null && echo "   Killed process $pid"
    done
    sleep 2
    echo "   ✓ All processes stopped"
else
    echo "   No running instances found"
fi

# Step 2: Remove plugin files
echo
echo "2. Removing plugin files..."
rm -f "$PLUGIN_DIR/edge_bookmarks_runner.py"
rm -f "$PLUGIN_DIR/bookmark_parser.py"
rm -f "$PLUGIN_DIR/search_engine.py"
rm -f "$PLUGIN_DIR/pinyin_matcher.py"
rm -f "$PLUGIN_DIR/config.py"
echo "   ✓ Plugin files removed"

# Step 3: Remove Python cache
echo
echo "3. Removing Python cache..."
rm -rf "$PLUGIN_DIR/__pycache__"
rm -f "$PLUGIN_DIR"/*.pyc
echo "   ✓ Cache removed"

# Step 4: Remove desktop files
echo
echo "4. Removing desktop files..."
rm -f "$PLUGIN_DIR/plasma-runner-edge-bookmarks.desktop"
rm -f "$DESKTOP_DIR/plasma-runner-edge-bookmarks.desktop"
rm -f "$DESKTOP_DIR/plasma-runner-krunner-edge-helper.desktop"
echo "   ✓ Desktop files removed"

# Step 5: Remove DBus service file
echo
echo "5. Removing DBus service file..."
rm -f "$DBUS_SERVICE_DIR/org.kde.plasma.runner.edgebookmarks.service"
echo "   ✓ DBus service file removed"

# Step 6: Remove log file
echo
echo "6. Removing log file..."
rm -f /tmp/edge_bookmarks.log
echo "   ✓ Log file removed"

# Step 7: Restart KRunner
echo
echo "7. Restarting KRunner..."
killall krunner 2>/dev/null || true
kquitapp5 krunner 2>/dev/null || kquitapp6 krunner 2>/dev/null || true
sleep 2
echo "   ✓ KRunner restarted"

echo
echo "=== Uninstallation Complete ==="
echo
echo "All plugin files, processes, and caches have been removed."
echo
echo "Note: Python dependencies were NOT removed."
echo "To remove them manually, run:"
echo "  pip3 uninstall pypinyin rapidfuzz dbus-python PyQt5"
echo
