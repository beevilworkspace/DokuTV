"""
Configuration management for YouTube Content Collector operations.
Centralizes environment variable lookups, API URLs, and default parameters.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class YouTubeCollectorConfig:
    """Configuration options for YouTube Content Collector."""
    api_key: str = ""
    fallback_file: Path = Path("data/fallback_playlist.json")
    api_base_url: str = "https://www.googleapis.com/youtube/v3/search"
    user_agent: str = "DokuTV_EN/1.0"
    search_orders: List[str] = field(default_factory=lambda: ["relevance", "viewCount", "rating"])

    @classmethod
    def from_env(
        cls,
        api_key: Optional[str] = None,
        fallback_file: Optional[Path] = None,
    ) -> "YouTubeCollectorConfig":
        """Instantiate config with settings populated from environment variables."""
        key = api_key or os.getenv("YOUTUBE_API_KEY", "")
        file_path = fallback_file or Path(os.getenv("FALLBACK_PLAYLIST_FILE", "data/fallback_playlist.json"))
        return cls(
            api_key=key,
            fallback_file=file_path,
        )
