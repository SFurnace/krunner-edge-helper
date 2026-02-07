"""
Configuration for Edge Bookmarks KRunner Plugin
"""
import os
from pathlib import Path

# Default bookmark file location
DEFAULT_BOOKMARK_PATH = os.path.expanduser(
    "~/.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Bookmarks"
)

# Trigger keyword for KRunner
TRIGGER_KEYWORD = "b"

# Search settings
MAX_RESULTS = 10
FUZZY_THRESHOLD = 60  # Minimum score for fuzzy matching (0-100)

# Cache settings
CACHE_ENABLED = True
CACHE_CHECK_INTERVAL = 2  # seconds

# Browser command
# Try Flatpak first, fallback to system installation
BROWSER_COMMANDS = [
    ["flatpak", "run", "com.microsoft.Edge"],
    ["microsoft-edge-stable"],
    ["microsoft-edge"],
    ["edge"],
]
