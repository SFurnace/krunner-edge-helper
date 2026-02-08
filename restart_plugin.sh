#!/bin/bash
# Diagnostic and restart script for KRunner Edge Helper

PLUGIN_DIR="$HOME/.local/share/krunner/dbusplugins/krunner-edge-helper"

echo "=== KRunner Edge Helper - Diagnostic & Restart ==="
echo

# Kill any running instances
echo "1. Stopping any running instances..."
PIDS=$(ps aux | grep "krunner_edge_helper.py" | grep -v grep | awk '{print $2}')
if [ -n "$PIDS" ]; then
    for pid in $PIDS; do
        kill $pid 2>/dev/null && echo "   Killed process $pid"
    done
else
    echo "   No running instances found"
fi
sleep 2

# Clear Python cache
echo
echo "2. Clearing Python cache..."
rm -rf "$PLUGIN_DIR/__pycache__"
rm -f "$PLUGIN_DIR"/*.pyc
echo "   ✓ Cache cleared"

# Start the plugin
echo
echo "3. Starting KRunner Edge Helper..."
python3 "$PLUGIN_DIR/krunner_edge_helper.py" > /tmp/krunner_edge_helper.log 2>&1 &
PLUGIN_PID=$!
sleep 2

# Check if running
if ps -p $PLUGIN_PID > /dev/null; then
    echo "   ✓ Plugin started (PID: $PLUGIN_PID)"
else
    echo "   ✗ Plugin failed to start"
    echo "   Check log: cat /tmp/krunner_edge_helper.log"
    exit 1
fi

# Test DBus
echo
echo "4. Testing DBus interface..."
TEST_RESULT=$(dbus-send --session --print-reply --dest=org.kde.krunner.edgehelper /EdgeHelper org.kde.krunner1.Match string:"b test" 2>&1)

if echo "$TEST_RESULT" | grep -q "bookmark_"; then
    echo "   ✓ DBus working - found results!"
    RESULT_COUNT=$(echo "$TEST_RESULT" | grep -c "bookmark_")
    echo "   Found $RESULT_COUNT bookmarks matching 'test'"
else
    echo "   ✗ DBus test failed"
    echo "   Error: $TEST_RESULT"
    exit 1
fi

# Restart KRunner
echo
echo "5. Restarting KRunner..."
kquitapp5 krunner 2>/dev/null || kquitapp6 krunner 2>/dev/null
sleep 2
echo "   ✓ KRunner restarted"

echo
echo "=== All checks passed! ==="
echo
echo "Now test in KRunner:"
echo "  1. Press Alt+Space (or Alt+F2)"
echo "  2. Type: b <search term>"
echo "  3. You should see matching bookmarks"
echo
echo "Troubleshooting:"
echo "  - Plugin log: cat /tmp/krunner_edge_helper.log"
echo "  - Plugin PID: $PLUGIN_PID"
echo "  - Stop plugin: kill $PLUGIN_PID"
echo "  - Restart: $0"
echo
