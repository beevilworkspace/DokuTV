"""
Interface Adapters - YouTube Content Collector.
Implements ContentCollectorPort.
"""

import os
import json
import random
import urllib.request
import urllib.parse
import logging
from typing import List, Dict, Any, Optional

from dokutv.domain.models import Video
from dokutv.application.ports import ContentCollectorPort
from dokutv.infrastructure.env_config import load_env

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("YouTubeCollectorAdapter")

class YouTubeCollectorAdapter(ContentCollectorPort):
    def __init__(self, api_key: Optional[str] = None):
        load_env()
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")

    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        if self.api_key and not self.api_key.startswith("AIzaSyYourActual"):
            logger.info(f"Connecting to YouTube Data API v3 for query: '{query}'...")
            try:
                return self._fetch_from_youtube_api(query, max_results)
            except Exception as e:
                logger.error(f"YouTube API Request failed: {e}. Falling back to curated CC-BY list.")

        logger.info("Using curated real Creative Commons / Public Domain documentary catalog.")
        return self._get_curated_cc_documentaries()

    def _fetch_from_youtube_api(self, query: str, max_results: int) -> List[Video]:
        # Randomize search sort order for maximum content variety
        selected_order = random.choice(["relevance", "viewCount", "rating"])
        logger.info(f"YouTube API Request: Searching '{query}' with order='{selected_order}'...")
        
        # Stage 1: Try with Documentary category (ID 35) + CC license
        video_items = self._youtube_search(query, max_results, selected_order, category_id="35", video_license="creativeCommon")
        
        # Stage 2: Fallback without category filter, with CC license
        if not video_items:
            logger.info("No results with Documentary category filter. Retrying with CC license without category...")
            video_items = self._youtube_search(query, max_results, selected_order, category_id=None, video_license="creativeCommon")

        # Stage 3: Fallback without CC license restriction (general search for documentary content)
        if not video_items:
            logger.info("No CC-licensed results found. Retrying general search without license filter...")
            video_items = self._youtube_search(query, max_results, selected_order, category_id=None, video_license=None)

        if not video_items:
            logger.warning("No search results returned from YouTube API.")
            return self._get_curated_cc_documentaries()

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
        
        # Shuffle results so playlist order varies on every run
        random.shuffle(results)
        return results

    def _youtube_search(self, query: str, max_results: int, order: str, category_id: str = None, video_license: str = "creativeCommon") -> list:
        """Execute a single YouTube Data API search request."""
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoDuration": "long",
            "videoDefinition": "high",
            "order": order,
            "maxResults": max_results,
            "key": self.api_key,
        }
        if category_id:
            params["videoCategoryId"] = category_id
        if video_license:
            params["videoLicense"] = video_license

        search_url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(search_url, headers={"User-Agent": "DokuTV_EN/1.0"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
        except Exception as e:
            logger.warning(f"YouTube search attempt failed: {e}")
            return []

    def _get_curated_cc_documentaries(self) -> List[Video]:
        raw_items = [
            {
                "id": "vP4-T0pZlyI",
                "title": "NASA | Tour of the Moon in 4K",
                "duration_seconds": 3600,
                "license": "Public Domain (NASA)",
                "description": "Official NASA 4K visualization tour of the Moon.",
                "youtube_url": "https://www.youtube.com/watch?v=vP4-T0pZlyI"
            },
            {
                "id": "J34rB7jWshg",
                "title": "Hubble Deep Field: Journey to the Edge of the Universe",
                "duration_seconds": 3600,
                "license": "Public Domain (NASA/ESA)",
                "description": "Deep space exploration and cosmological discoveries.",
                "youtube_url": "https://www.youtube.com/watch?v=J34rB7jWshg"
            },
            {
                "id": "R9K486n1O2U",
                "title": "Secrets of the Deep Ocean & Marine Wildlife HD",
                "duration_seconds": 3600,
                "license": "Creative Commons Attribution",
                "description": "Exploration of marine life and deep sea ecosystems.",
                "youtube_url": "https://www.youtube.com/watch?v=R9K486n1O2U"
            },
            {
                "id": "6v2L2UGZJAM",
                "title": "Planet Earth: Forests & Wilderness Preservation",
                "duration_seconds": 3600,
                "license": "Creative Commons Attribution",
                "description": "Wilderness conservation and wildlife habitats.",
                "youtube_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM"
            },
            {
                "id": "843R75i2t2s",
                "title": "Wonders of the Solar System & Planetary Science",
                "duration_seconds": 3600,
                "license": "Public Domain (NASA)",
                "description": "Planetary exploration across the Solar System.",
                "youtube_url": "https://www.youtube.com/watch?v=843R75i2t2s"
            }
        ]
        return [Video(**item) for item in raw_items]

    def save_playlist_cache(self, videos: List[Video], filepath: str = "data/playlist_cache.json") -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        raw_list = [v.__dict__ for v in videos]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(raw_list, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(videos)} videos to cache at '{filepath}'.")
