import html
import json
import random
import re
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Tuple, Optional, Dict

from dokutv.domain.models import Video
from dokutv.domain.topics import is_valid_documentary
from dokutv.adapters.collector.collector_config import YouTubeCollectorConfig

logger = logging.getLogger(__name__)


def parse_iso8601_duration(duration_str: str) -> int:
    """
    Parse ISO 8601 duration format (e.g. 'PT1H23M45S', 'PT45M', 'PT2H', 'PT30S') into seconds.
    Returns 3600 as fallback if string cannot be parsed.
    """
    if not duration_str:
        return 3600
    pattern = re.compile(r'P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration_str)
    if not match:
        return 3600
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)
    total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
    return total_seconds if total_seconds > 0 else 3600


class YouTubeApiClient:
    """HTTP Client interacting with YouTube Data API v3."""

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

        # Stage 2: Fallback without category filter, STILL strictly requiring CC license
        if not video_items:
            logger.info("No CC results in Documentary category (35). Retrying with CC license across all categories...")
            video_items, is_rate_limited = self._youtube_search(
                query, max_results, selected_order, category_id=None, video_license="creativeCommon"
            )
            if is_rate_limited:
                return []

        if not video_items:
            logger.warning("No Creative Commons licensed results found on YouTube API. Falling back to curated catalog.")
            return []

        video_ids = [item["id"]["videoId"] for item in video_items if "id" in item and "videoId" in item.get("id", {})]
        durations = self._fetch_video_details(video_ids)

        results = []
        for item in video_items:
            v_id = item["id"]["videoId"]
            snippet = item["snippet"]
            title = html.unescape(snippet["title"])
            description = html.unescape(snippet.get("description", ""))

            # Filter out blacklisted sleep/chill/ambient videos
            if not is_valid_documentary(title, description):
                logger.info(f"🚫 Filtering out unsuited video '{title}' (matches sleep/chill/relaxing blacklist).")
                continue

            dur_sec = durations.get(v_id, 3600)
            results.append(Video(
                id=v_id,
                title=title,
                duration_seconds=dur_sec,
                license="creativeCommon",
                description=description,
                youtube_url=f"https://www.youtube.com/watch?v={v_id}"
            ))

        random.shuffle(results)
        return results

    def _fetch_video_details(self, video_ids: List[str]) -> Dict[str, int]:
        """
        Batch query YouTube Data API v3 videos endpoint for exact video durations (contentDetails).
        Returns a mapping of video_id -> duration_seconds.
        """
        if not video_ids or not self.is_api_key_valid():
            return {}

        videos_api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "contentDetails",
            "id": ",".join(video_ids[:50]),
            "key": self.config.api_key,
        }
        url = f"{videos_api_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": self.config.user_agent})
        
        durations: Dict[str, int] = {}
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("items", []):
                v_id = item.get("id")
                content_details = item.get("contentDetails", {})
                iso_duration = content_details.get("duration", "")
                if v_id and iso_duration:
                    durations[v_id] = parse_iso8601_duration(iso_duration)
            logger.info(f"Retrieved exact video durations for {len(durations)} videos from YouTube API.")
        except Exception as e:
            logger.warning(f"Failed to fetch video details / durations from YouTube API: {e}")

        return durations

    def _youtube_search(
        self,
        query: str,
        max_results: int,
        order: str,
        category_id: Optional[str] = None,
        video_license: str = "creativeCommon",
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
            "videoLicense": video_license or "creativeCommon",
            "key": self.config.api_key,
        }
        if category_id:
            params["videoCategoryId"] = category_id

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

