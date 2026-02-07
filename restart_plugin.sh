#!/bin/bash
# Diagnostic and restart script for Edge Bookmarks KRunner Plugin

echo "=== Edge Bookmarks KRunner Plugin - Diagnostic & Restart ==="
echo

# Kill any running instances
echo "1. Stopping any running instances..."
for pid in $(ps aux | grep "edge_bookmarks_runner.py" | grep -v grep | awk '{print $2}'); do
    kill $pid 2>/dev/null
    echo "   Killed process $pid"
done
sleep 1

# Start the plugin
echo
echo "2. Starting Edge Bookmarks plugin..."
~/.local/share/krunner/dbusplugins/edge_bookmarks_runner.py > /tmp/edge_bookmarks.log 2>&1 &
PLUGIN_PID=$!
sleep 2

# Check if running
if ps -p $PLUGIN_PID > /dev/null; then
    echo "   ✓ Plugin started (PID: $PLUGIN_PID)"
else
    echo "   ✗ Plugin failed to start"
    echo "   Check log: cat /tmp/edge_bookmarks.log"
    exit 1
fi

# Test DBus
echo
echo "3. Testing DBus interface..."
TEST_RESULT=$(dbus-send --session --print-reply --dest=org.kde.plasma.runner.edgebookmarks /EdgeBookmarks org.kde.krunner1.Match string:"b test" 2>&1)

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
echo "4. Restarting KRunner..."
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
echo "  - Plugin log: cat /tmp/edge_bookmarks.log"
echo "  - Plugin PID: $PLUGIN_PID"
echo "  - Stop plugin: kill $PLUGIN_PID"
echo "  - Restart: $0"
echo
