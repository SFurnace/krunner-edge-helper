"""
Edge Bookmark Parser
Parses Microsoft Edge (Chromium-based) bookmark JSON file
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class Bookmark:
    """Represents a single bookmark"""
    
    def __init__(self, name: str, url: str, folder: str = "", date_added: Optional[int] = None):
        self.name = name
        self.url = url
        self.folder = folder
        self.date_added = date_added
    
    def __repr__(self):
        return f"Bookmark(name='{self.name}', url='{self.url}', folder='{self.folder}')"


class BookmarkParser:
    """Parser for Edge/Chrome bookmark JSON files"""
    
    def __init__(self, bookmark_path: str):
        self.bookmark_path = Path(bookmark_path)
        self.bookmarks: List[Bookmark] = []
        self._last_modified: Optional[float] = None
    
    def parse(self) -> List[Bookmark]:
        """Parse bookmarks from the JSON file"""
        if not self.bookmark_path.exists():
            raise FileNotFoundError(f"Bookmark file not found: {self.bookmark_path}")
        
        with open(self.bookmark_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.bookmarks = []
        
        # Parse bookmark roots (bookmark_bar, other, synced)
        roots = data.get('roots', {})
        for root_name, root_data in roots.items():
            if isinstance(root_data, dict) and root_data.get('type') == 'folder':
                self._parse_folder(root_data, folder_path="")
        
        # Update last modified time
        self._last_modified = self.bookmark_path.stat().st_mtime
        
        return self.bookmarks
    
    def _parse_folder(self, folder: Dict, folder_path: str):
        """Recursively parse a bookmark folder"""
        folder_name = folder.get('name', '')
        current_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
        
        children = folder.get('children', [])
        for child in children:
            child_type = child.get('type')
            
            if child_type == 'url':
                # It's a bookmark
                bookmark = Bookmark(
                    name=child.get('name', ''),
                    url=child.get('url', ''),
                    folder=current_path,
                    date_added=child.get('date_added')
                )
                self.bookmarks.append(bookmark)
            
            elif child_type == 'folder':
                # It's a subfolder, recurse
                self._parse_folder(child, current_path)
    
    def is_modified(self) -> bool:
        """Check if the bookmark file has been modified since last parse"""
        if not self.bookmark_path.exists():
            return False
        
        if self._last_modified is None:
            return True
        
        current_mtime = self.bookmark_path.stat().st_mtime
        return current_mtime > self._last_modified
    
    def get_bookmarks(self) -> List[Bookmark]:
        """Get cached bookmarks, reparse if file was modified"""
        if not self.bookmarks or self.is_modified():
            return self.parse()
        return self.bookmarks
