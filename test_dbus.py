#!/usr/bin/env python3
"""
Minimal DBus test for KRunner signature
"""
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

DBusGMainLoop(set_as_default=True)

class TestRunner(dbus.service.Object):
    def __init__(self):
        session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.kde.test.runner", session_bus)
        super().__init__(bus_name, "/TestRunner")
    
    @dbus.service.method("org.kde.krunner1", in_signature='s', out_signature='a(sssida{sv})')
    def Match(self, query):
        """Test Match method"""
        # Return one simple match
        matches = [
            ("id1", "Test 1", "icon", 100, {"subtext": "test"}),
            ("id2", "Test 2", "icon", 90, {"subtext": "test2"}),
        ]
        return matches

if __name__ == '__main__':
    runner = TestRunner()
    print("Test runner started")
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
