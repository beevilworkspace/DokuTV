"""
Persistence component for curated fallback documentaries.
Reads fallback JSON playlist from disk as the single source of truth.
"""

import json
import random
import logging
from pathlib import Path
from typing import List

from dokutv.domain.models import Video

logger = logging.getLogger(__name__)


class FallbackPlaylistStore:
    """Manages curated fallback documentary content from disk."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load_curated_videos(self) -> List[Video]:
        """Load curated videos from disk fallback JSON file."""
        if not self.file_path.exists():
            logger.error(f"Fallback playlist file '{self.file_path}' does not exist!")
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
            logger.info(f"Loaded {len(raw_items)} curated fallback documentaries from '{self.file_path}'.")
            curated_videos = [Video(**item) for item in raw_items]
            random.shuffle(curated_videos)
            return curated_videos
        except (json.JSONDecodeError, OSError, KeyError, TypeError) as e:
            logger.error(f"Error loading fallback playlist '{self.file_path}': {e}")
            return []
