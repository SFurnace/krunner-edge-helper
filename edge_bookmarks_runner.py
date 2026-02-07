#!/usr/bin/env python3
"""
Edge Bookmarks KRunner Plugin
DBus-based plugin for searching Edge bookmarks in KRunner
"""
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess
import sys
import os
from typing import List, Tuple

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bookmark_parser import BookmarkParser, Bookmark
from search_engine import SearchEngine
import config


# DBus interface names
SERVICE_NAME = "org.kde.plasma.runner.edgebookmarks"
OBJECT_PATH = "/EdgeBookmarks"
IFACE = "org.kde.krunner1"


class EdgeBookmarksRunner(dbus.service.Object):
    """KRunner plugin for Edge bookmarks"""
    
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(SERVICE_NAME, session_bus)
        super().__init__(bus_name, OBJECT_PATH)
        
        # Initialize components
        self.parser = BookmarkParser(config.DEFAULT_BOOKMARK_PATH)
        self.search_engine = SearchEngine()
        self.bookmarks = []
        
        # Load bookmarks
        self._load_bookmarks()
        
        print(f"Edge Bookmarks Runner initialized with {len(self.bookmarks)} bookmarks")
    
    def _load_bookmarks(self):
        """Load bookmarks from file"""
        try:
            self.bookmarks = self.parser.get_bookmarks()
            print(f"Loaded {len(self.bookmarks)} bookmarks")
        except FileNotFoundError:
            print(f"Warning: Bookmark file not found at {config.DEFAULT_BOOKMARK_PATH}")
            self.bookmarks = []
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
            self.bookmarks = []
    
    @dbus.service.method(IFACE, in_signature='s', out_signature='a(sssida{sv})', async_callbacks=('ok_callback', 'err_callback'))
    def Match(self, query: str, ok_callback, err_callback):
        """
        Match query against bookmarks
        Returns: array of (id, text, icon, relevance, properties)
        - relevance: int32 (0 to 100)
        """
        try:
            # Check if query starts with trigger keyword
            if not query.startswith(config.TRIGGER_KEYWORD + " "):
                return ok_callback([])
            
            # Remove trigger keyword
            search_query = query[len(config.TRIGGER_KEYWORD) + 1:].strip()
            
            if not search_query:
                return ok_callback([])
            
            # Reload bookmarks if modified
            if self.parser.is_modified():
                self._load_bookmarks()
            
            # Search bookmarks
            results = self.search_engine.search(self.bookmarks, search_query)
            
            # Convert to KRunner format
            matches = []
            for i, (bookmark, score) in enumerate(results):
                match_id = f"bookmark_{i}_{bookmark.url}"
                
                # Format display text
                text = bookmark.name
                if bookmark.folder:
                    subtext = f"{bookmark.folder} | {bookmark.url}"
                else:
                    subtext = bookmark.url
                
                # Normalize relevance (0 to 100) as int32
                relevance = int(min(score, 100))
                
                # Relevance score as double (0.0 to 1.0)
                relevance_score = min(score / 100.0, 1.0)
                
                # Icon
                icon = 'internet-web-browser'
                
                # Properties dictionary
                properties = {
                    'subtext': subtext,
                    'urls': [bookmark.url]
                }
                
                # Create match tuple: (id, text, icon, match_type(int), relevance(double), properties(dict))
                match = (
                    match_id,
                    text,
                    icon,
                    relevance,
                    relevance_score,
                    properties
                )
                matches.append(match)
            
            return ok_callback(matches)
            
        except Exception as e:
            print(f"Error in Match: {e}")
            import traceback
            traceback.print_exc()
            return ok_callback([])
    
    @dbus.service.method(IFACE, in_signature='ss', out_signature='')
    def Run(self, match_id: str, action_id: str):
        """
        Execute the selected match
        Opens the bookmark in Edge browser
        """
        # Extract URL from match_id
        # Format: bookmark_<index>_<url>
        parts = match_id.split('_', 2)
        if len(parts) < 3:
            return
        
        url = parts[2]
        
        # Try browser commands in order
        for browser_cmd in config.BROWSER_COMMANDS:
            try:
                cmd = browser_cmd + [url]
                subprocess.Popen(cmd, 
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)
                # Uncomment for debugging:
                # print(f"Opened bookmark with {browser_cmd[0]}")
                return
            except FileNotFoundError:
                continue
            except Exception as e:
                # Uncomment for debugging:
                # print(f"Error launching {browser_cmd[0]}: {e}")
                continue
        
        # Fallback to xdg-open
        try:
            subprocess.Popen(['xdg-open', url],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            # Uncomment for debugging:
            # print(f"Opened bookmark with xdg-open")
        except Exception as e:
            # Uncomment for debugging:
            # print(f"Error opening URL: {e}")
            pass
    
    @dbus.service.method(IFACE, in_signature='s', out_signature='a(sss)')
    def Actions(self, match_id: str):
        """
        Return additional actions for a match
        Currently no additional actions
        """
        return []


def main():
    """Main entry point"""
    runner = EdgeBookmarksRunner()
    
    loop = GLib.MainLoop()
    
    print("Edge Bookmarks KRunner plugin running...")
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        loop.quit()


if __name__ == '__main__':
    main()
