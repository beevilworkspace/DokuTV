"""
YouTube Data API v3 HTTP client component.
Encapsulates video search requests and 3-stage fallback strategies.
"""

import json
import random
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Tuple, Optional

from dokutv.domain.models import Video
from dokutv.adapters.collector.collector_config import YouTubeCollectorConfig

logger = logging.getLogger(__name__)


class YouTubeApiClient:
    """Handles HTTP communication with YouTube Data API v3 search endpoints."""

    def __init__(self, config: YouTubeCollectorConfig):
        self.config = config

    def is_api_key_valid(self) -> bool:
        """Check if configured API key is valid (not empty or default placeholder)."""
        return bool(self.config.api_key and not self.config.api_key.startswith("AIzaSyYourActual"))

    def search_videos(self, query: str, max_results: int = 30) -> List[Video]:
        """Execute multi-stage search strategy for Creative Commons / documentary content."""
        if not self.is_api_key_valid():
            return []

        selected_order = random.choice(list(self.config.search_orders))
        logger.info(f"Connecting to YouTube Data API v3 for query: '{query}' (order='{selected_order}')...")

        # Stage 1: Documentary category (35) + Creative Commons license
        video_items, is_rate_limited = self._youtube_search(
            query, max_results, selected_order, category_id="35", video_license="creativeCommon"
        )
        if is_rate_limited:
            logger.warning("YouTube API Rate Limited (HTTP 429 / 403). Skipping online search stages.")
            return []

        # Stage 2: Fallback without category filter, with CC license
        if not video_items:
            logger.info("No results with Documentary category. Retrying with CC license without category...")
            video_items, is_rate_limited = self._youtube_search(
                query, max_results, selected_order, category_id=None, video_license="creativeCommon"
            )
            if is_rate_limited:
                return []

        # Stage 3: Fallback general search without license filter
        if not video_items:
            logger.info("No CC-licensed results found. Retrying general search without license filter...")
            video_items, _ = self._youtube_search(
                query, max_results, selected_order, category_id=None, video_license=None
            )

        if not video_items:
            logger.warning("No search results returned from YouTube API.")
            return []

        results = []
        for item in video_items:
            v_id = item["id"]["videoId"]
            snippet = item["snippet"]
            results.append(Video(
                id=v_id,
                title=snippet["title"],
                duration_seconds=3600,
                license="creativeCommon",
                description=snippet.get("description", ""),
                youtube_url=f"https://www.youtube.com/watch?v={v_id}"
            ))

        random.shuffle(results)
        return results

    def _youtube_search(
        self,
        query: str,
        max_results: int,
        order: str,
        category_id: Optional[str] = None,
        video_license: Optional[str] = "creativeCommon",
    ) -> Tuple[List[dict], bool]:
        """Execute a single YouTube Data API search request. Returns (items_list, is_rate_limited)."""
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoDuration": "long",
            "videoDefinition": "high",
            "order": order,
            "maxResults": max_results,
            "key": self.config.api_key,
        }
        if category_id:
            params["videoCategoryId"] = category_id
        if video_license:
            params["videoLicense"] = video_license

        search_url = f"{self.config.api_base_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(search_url, headers={"User-Agent": self.config.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", []), False
        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode("utf-8", errors="replace")
            if http_err.code in (403, 429):
                logger.warning(f"YouTube API Error (HTTP {http_err.code}): {err_body}")
                return [], True
            logger.warning(f"YouTube search attempt HTTP error {http_err.code}: {err_body}")
            return [], False
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"YouTube search attempt failed: {e}")
            return [], False
