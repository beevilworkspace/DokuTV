"""
Interface Adapters - YouTube Content Collector.
Implements ContentCollectorPort.
Pure infrastructure adapter fetching video candidates from YouTube API or fallback storage.
"""

import logging
from typing import Any, List, Optional, Set

from dokutv.domain.models import Video
from dokutv.domain.topics import get_random_topic
from dokutv.application.ports import ContentCollectorPort
from dokutv.adapters.collector.collector_config import YouTubeCollectorConfig
from dokutv.adapters.collector.fallback_playlist_store import FallbackPlaylistStore
from dokutv.adapters.collector.youtube_api_client import YouTubeApiClient

logger = logging.getLogger(__name__)


class YouTubeCollectorAdapter(ContentCollectorPort):
    """Facade orchestrating documentary content collection operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[YouTubeCollectorConfig] = None,
        api_client: Optional[YouTubeApiClient] = None,
        fallback_store: Optional[FallbackPlaylistStore] = None,
    ):
        self.config = config or YouTubeCollectorConfig.from_env(api_key=api_key)
        self.api_client = api_client or YouTubeApiClient(self.config)
        self.fallback_store = fallback_store or FallbackPlaylistStore(self.config.fallback_file)

    @property
    def api_key(self) -> str:
        return self.config.api_key

    @api_key.setter
    def api_key(self, val: str) -> None:
        self.config.api_key = val

    def get_next_video(self, query: str = "documentary", exclude_ids: Optional[Any] = None) -> Optional[Video]:
        """Fetch candidate videos and pick one whose ID is not in exclude_ids."""
        exclude_set = self._normalize_exclude_ids(exclude_ids)
        candidates = self.search_cc_documentaries(query=query, max_results=30)

        for video in candidates:
            if video.id not in exclude_set:
                return video

        # Retry online search with alternative categories on YouTube API before resorting to fallback_store
        if self.api_client.is_api_key_valid():
            logger.info(f"No non-excluded CC results for '{query}'. Retrying online search across alternative categories...")
            for _ in range(4):
                alt_topic = get_random_topic()
                try:
                    alt_candidates = self.api_client.search_videos(alt_topic, max_results=30)
                    for video in alt_candidates:
                        if video.id not in exclude_set:
                            logger.info(f"✅ Found online CC video '{video.title}' from alternative category topic '{alt_topic}'.")
                            return video
                except Exception as e:
                    logger.warning(f"Alternative category search for '{alt_topic}' failed: {e}")

        # Fallback to curated list ONLY if online API retries across categories return nothing
        logger.info("Using curated Creative Commons / Public Domain documentary catalog as last resort.")
        curated = self.fallback_store.load_curated_videos()
        for video in curated:
            if video.id not in exclude_set:
                return video

        return curated[0] if curated else None

    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        """Search online API for documentaries."""
        if self.api_client.is_api_key_valid():
            try:
                results = self.api_client.search_videos(query, max_results)
                if results:
                    return results
            except Exception as e:
                logger.error(f"YouTube API Request failed: {e}.")

        return []


    def _normalize_exclude_ids(self, exclude_ids: Optional[Any]) -> Set[str]:
        """Convert string, set, list, or tuple exclude_ids parameter into a set."""
        if isinstance(exclude_ids, str):
            return {exclude_ids}
        if isinstance(exclude_ids, (set, list, tuple)):
            return set(exclude_ids)
        return set()
