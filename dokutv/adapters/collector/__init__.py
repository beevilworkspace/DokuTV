"""
YouTube Content Collector Subpackage.
Exposes modular YouTube Data API v3 collector components.
"""

from dokutv.adapters.collector.collector_config import YouTubeCollectorConfig
from dokutv.adapters.collector.fallback_playlist_store import FallbackPlaylistStore
from dokutv.adapters.collector.youtube_api_client import YouTubeApiClient
from dokutv.adapters.collector.youtube_collector_adapter import YouTubeCollectorAdapter

__all__ = [
    "YouTubeCollectorConfig",
    "FallbackPlaylistStore",
    "YouTubeApiClient",
    "YouTubeCollectorAdapter",
]
