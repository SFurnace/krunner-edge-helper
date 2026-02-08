#!/bin/bash
# Uninstallation script for KRunner Edge Helper

set -e

PLUGIN_DIR="$HOME/.local/share/krunner/dbusplugins/krunner-edge-helper"
DBUSPLUGINS_DIR="$HOME/.local/share/krunner/dbusplugins"
DBUS_SERVICE_DIR="$HOME/.local/share/dbus-1/services"

echo "=== KRunner Edge Helper Uninstallation ==="
echo

# Step 1: Stop all running processes FIRST
echo "1. Stopping all running instances..."
RUNNING_PIDS=$(ps aux | grep "krunner_edge_helper.py" | grep -v grep | awk '{print $2}')
if [ -n "$RUNNING_PIDS" ]; then
    for pid in $RUNNING_PIDS; do
        kill $pid 2>/dev/null && echo "   Killed process $pid"
    done
    sleep 2
    echo "   ✓ All processes stopped"
else
    echo "   No running instances found"
fi

# Step 2: Remove plugin directory
echo
echo "2. Removing plugin directory..."
rm -rf "$PLUGIN_DIR"
echo "   ✓ Plugin directory removed"

# Step 3: Remove desktop file
echo
echo "3. Removing desktop file..."
rm -f "$DBUSPLUGINS_DIR/krunner-edge-helper.desktop"
echo "   ✓ Desktop file removed"

# Step 4: Remove DBus service file
echo
echo "4. Removing DBus service file..."
rm -f "$DBUS_SERVICE_DIR/org.kde.krunner.edgehelper.service"
echo "   ✓ DBus service file removed"

# Step 5: Remove log file
echo
echo "5. Removing log file..."
rm -f /tmp/krunner_edge_helper.log
echo "   ✓ Log file removed"

# Step 6: Restart KRunner
echo
echo "6. Restarting KRunner..."
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
