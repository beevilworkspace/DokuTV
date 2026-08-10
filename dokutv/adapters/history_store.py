"""
Infrastructure Adapter - JSON Play History Store.
Implements PlayHistoryPort for persisting broadcast video history to a JSON file.
"""

import json
import logging
import os
import threading
from typing import List
from dokutv.domain.models import PlayHistoryEntry
from dokutv.application.ports.history_port import PlayHistoryPort

logger = logging.getLogger("JsonHistoryStoreAdapter")


class JsonHistoryStoreAdapter(PlayHistoryPort):
    """Adapter for persisting and reading video play history from a JSON file."""

    def __init__(self, file_path: str = "data/history.json"):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create parent directory and empty JSON file if it does not exist."""
        dirname = os.path.dirname(self.file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except Exception as e:
                logger.error(f"Failed to initialize history file at '{self.file_path}': {e}")

    def add_entry(self, entry: PlayHistoryEntry) -> None:
        """Add a video play history entry to the JSON file."""
        with self._lock:
            history_data = self._read_raw_json()
            history_data.append(entry.to_dict())
            self._write_raw_json(history_data)
            logger.info(f"Recorded video play history: '{entry.title}' (ID: {entry.video_id})")

    def get_history(self) -> List[PlayHistoryEntry]:
        """Retrieve all recorded play history entries from the JSON file."""
        with self._lock:
            raw_data = self._read_raw_json()
            entries: List[PlayHistoryEntry] = []
            for item in raw_data:
                try:
                    entries.append(PlayHistoryEntry.from_dict(item))
                except Exception as e:
                    logger.warning(f"Skipping malformed history entry in '{self.file_path}': {e}")
            return entries

    def clear_history(self) -> None:
        """Clear all play history entries from the JSON file."""
        with self._lock:
            self._write_raw_json([])
            logger.info(f"Cleared play history file at '{self.file_path}'.")

    def _read_raw_json(self) -> List[dict]:
        """Internal helper to read raw JSON list from file."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                logger.warning(f"History file '{self.file_path}' does not contain a JSON list.")
                return []
        except Exception as e:
            logger.error(f"Error reading history file '{self.file_path}': {e}")
            return []

    def _write_raw_json(self, data: List[dict]) -> None:
        """Internal helper to write raw JSON list to file."""
        try:
            dirname = os.path.dirname(self.file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing history file '{self.file_path}': {e}")
