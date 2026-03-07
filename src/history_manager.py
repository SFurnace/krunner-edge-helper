"""
History Manager for KRunner Edge Helper
Manages user selection history for personalized ranking
"""
import json
import os
import time
import math
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict

import config


@dataclass
class HistoryRecord:
    """Single history record for a query-bookmark pair"""
    name: str
    folder: str
    frequency: int
    last_used: int
    first_used: int

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryRecord':
        return cls(**data)


class HistoryManager:
    """Manages bookmark selection history"""

    DATA_VERSION = 1

    def __init__(self):
        # Store history in plugin directory for unified management
        # This allows history to be cleaned up when uninstalling the plugin
        self.data_dir = Path(os.path.expanduser(
            '~/.local/share/krunner/dbusplugins/krunner-edge-helper'
        ))
        self.data_file = self.data_dir / 'history.json'
        self.data: Dict = {"version": self.DATA_VERSION, "records": {}}

        self._ensure_data_dir()
        self._load()

    def _ensure_data_dir(self):
        """Create data directory if not exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Set directory permissions to 700 (only owner can read/write/execute)
        self.data_dir.chmod(0o700)

    def _load(self):
        """Load history from file"""
        if not self.data_file.exists():
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                if loaded.get('version') == self.DATA_VERSION:
                    self.data = loaded
        except (json.JSONDecodeError, IOError):
            self.data = {"version": self.DATA_VERSION, "records": {}}

    def _save(self):
        """Save history to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            # Set file permissions to 600 (only owner can read/write)
            self.data_file.chmod(0o600)
        except IOError as e:
            print(f"Error saving history: {e}")

    def record_selection(self, query: str, bookmark):
        """Record a bookmark selection"""
        if not config.HISTORY_ENABLED:
            return

        query = query.strip().lower()
        url = bookmark.url

        if not query or not url:
            return

        if query not in self.data["records"]:
            self.data["records"][query] = {}

        now = int(time.time())

        if url not in self.data["records"][query]:
            # New record
            self.data["records"][query][url] = {
                "name": bookmark.name,
                "folder": bookmark.folder,
                "frequency": 1,
                "last_used": now,
                "first_used": now
            }
        else:
            # Update existing record
            record = self.data["records"][query][url]
            record["frequency"] += 1
            record["last_used"] = now
            record["name"] = bookmark.name
            record["folder"] = bookmark.folder

        self._save()

    def get_record(self, query: str, url: str) -> Optional[HistoryRecord]:
        """Get history record for a query-bookmark pair"""
        query = query.strip().lower()
        if query not in self.data["records"]:
            return None
        if url not in self.data["records"][query]:
            return None
        return HistoryRecord.from_dict(self.data["records"][query][url])

    def get_weight(self, query: str, url: str) -> float:
        """Calculate history weight for a query-bookmark pair"""
        record = self.get_record(query, url)
        if record is None:
            return 0.0

        return self._calculate_weight(record)

    def _calculate_weight(self, record: HistoryRecord) -> float:
        """Calculate history weight from record"""
        # Frequency factor (logarithmic compression)
        freq_factor = math.log1p(record.frequency) / math.log1p(20)
        freq_factor = min(freq_factor, 1.0)

        # Time decay factor
        days_since = (time.time() - record.last_used) / 86400
        time_factor = 0.5 ** (days_since / config.HISTORY_HALF_LIFE_DAYS)

        # Combined weight
        weight = (freq_factor * 0.6) + (time_factor * 0.4)
        return min(weight, 1.0)

    def cleanup_old_records(self) -> int:
        """Remove old and infrequently used records"""
        now = int(time.time())
        records_to_remove = []

        for query, urls in list(self.data["records"].items()):
            urls_to_remove = []

            for url, record in list(urls.items()):
                days_since_use = (now - record["last_used"]) / 86400

                # Remove if too old
                if days_since_use > config.HISTORY_RETENTION_DAYS:
                    urls_to_remove.append(url)
                # Remove if used only once and moderately old
                elif record["frequency"] == 1 and days_since_use > 90:
                    urls_to_remove.append(url)

            for url in urls_to_remove:
                del urls[url]

            if not urls:
                records_to_remove.append(query)

        for query in records_to_remove:
            del self.data["records"][query]

        if records_to_remove or any(
            len(urls) < len(self.data["records"].get(query, {}))
            for query in self.data["records"]
        ):
            self._save()

        return len(records_to_remove)

    def get_stats(self) -> dict:
        """Get history statistics"""
        total_queries = len(self.data["records"])
        total_bookmarks = sum(
            len(urls) for urls in self.data["records"].values()
        )

        return {
            "total_queries": total_queries,
            "total_bookmarks": total_bookmarks,
            "version": self.data.get("version", 1)
        }
