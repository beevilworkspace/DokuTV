"""
Interface Adapters - YouTube Content Collector.
Implements ContentCollectorPort.
Orchestrates YouTube Data API search, video candidate pool, and fallback playlist storage.
"""

import logging
from typing import Any, List, Optional, Set

from dokutv.domain.models import Video
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

        self.video_pool: List[Video] = []

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

        # Combine fresh candidates + video pool
        all_candidates = candidates + [v for v in self.video_pool if v not in candidates]

        for video in all_candidates:
            if video.id not in exclude_set:
                return video

        # Fallback to curated list if all candidates are excluded
        curated = self.fallback_store.load_curated_videos()
        for video in curated:
            if video.id not in exclude_set:
                return video

        return curated[0] if curated else None

    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        """Search online API for documentaries or fall back to local video pool / fallback catalog."""
        if self.api_client.is_api_key_valid():
            try:
                results = self.api_client.search_videos(query, max_results)
                if results:
                    existing_ids = {v.id for v in self.video_pool}
                    for v in results:
                        if v.id not in existing_ids:
                            self.video_pool.append(v)
                    return results
            except Exception as e:
                logger.error(f"YouTube API Request failed: {e}. Falling back to video pool / curated list.")

        if self.video_pool:
            logger.info(f"Using {len(self.video_pool)} videos from local video pool.")
            return self.video_pool

        logger.info("Using curated Creative Commons / Public Domain documentary catalog.")
        return self.fallback_store.load_curated_videos()

    def _normalize_exclude_ids(self, exclude_ids: Optional[Any]) -> Set[str]:
        """Convert string, set, list, or tuple exclude_ids parameter into a set."""
        if isinstance(exclude_ids, str):
            return {exclude_ids}
        if isinstance(exclude_ids, (set, list, tuple)):
            return set(exclude_ids)
        return set()
