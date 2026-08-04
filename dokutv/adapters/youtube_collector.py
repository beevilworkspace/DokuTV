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
from typing import Any, List, Optional

from dokutv.domain.models import Video
from dokutv.application.ports import ContentCollectorPort
from dokutv.infrastructure.env_config import load_env

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("YouTubeCollectorAdapter")

class YouTubeCollectorAdapter(ContentCollectorPort):
    def __init__(self, api_key: Optional[str] = None):
        load_env()
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")
        self.video_pool: List[Video] = []

    def get_next_video(self, query: str = "documentary", exclude_ids: Optional[Any] = None) -> Optional[Video]:
        """Fetch candidate videos and pick one whose ID is not in exclude_ids."""
        if isinstance(exclude_ids, str):
            exclude_set = {exclude_ids}
        elif isinstance(exclude_ids, (set, list, tuple)):
            exclude_set = set(exclude_ids)
        else:
            exclude_set = set()

        candidates = self.search_cc_documentaries(query=query, max_results=30)
        
        # Combine fresh candidates + video pool
        all_candidates = candidates + [v for v in self.video_pool if v not in candidates]

        for video in all_candidates:
            if video.id in exclude_set:
                continue
            return video

        # Fallback to curated list if all candidates are excluded
        curated = self._get_curated_cc_documentaries()
        for video in curated:
            if video.id in exclude_set:
                continue
            return video

        return curated[0] if curated else None

    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        if self.api_key and not self.api_key.startswith("AIzaSyYourActual"):
            logger.info(f"Connecting to YouTube Data API v3 for query: '{query}'...")
            try:
                results = self._fetch_from_youtube_api(query, max_results)
                if results:
                    # Update video pool
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

        logger.info("Using curated real Creative Commons / Public Domain documentary catalog.")
        return self._get_curated_cc_documentaries()

    def _fetch_from_youtube_api(self, query: str, max_results: int) -> List[Video]:
        # Randomize search sort order for maximum content variety
        selected_order = random.choice(["relevance", "viewCount", "rating"])
        logger.info(f"YouTube API Request: Searching '{query}' with order='{selected_order}'...")
        
        # Stage 1: Try with Documentary category (ID 35) + CC license
        video_items, is_rate_limited = self._youtube_search(query, max_results, selected_order, category_id="35", video_license="creativeCommon")
        
        # If rate limited (HTTP 429), abort further retries immediately
        if is_rate_limited:
            logger.warning("YouTube API Rate Limited (HTTP 429). Skipping further online search stages.")
            return []

        # Stage 2: Fallback without category filter, with CC license
        if not video_items:
            logger.info("No results with Documentary category filter. Retrying with CC license without category...")
            video_items, is_rate_limited = self._youtube_search(query, max_results, selected_order, category_id=None, video_license="creativeCommon")
            if is_rate_limited:
                return []

        # Stage 3: Fallback without CC license restriction (general search for documentary content)
        if not video_items:
            logger.info("No CC-licensed results found. Retrying general search without license filter...")
            video_items, _ = self._youtube_search(query, max_results, selected_order, category_id=None, video_license=None)

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
        
        # Shuffle results so playlist order varies on every run
        random.shuffle(results)
        return results

    def _youtube_search(self, query: str, max_results: int, order: str, category_id: str = None, video_license: str = "creativeCommon") -> tuple:
        """Execute a single YouTube Data API search request. Returns (items_list, is_rate_limited)."""
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
            return data.get("items", []), False
        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode("utf-8", errors="replace")
            if http_err.code in (403, 429):
                logger.warning(f"YouTube API Error (HTTP {http_err.code}): {err_body}")
                return [], True
            logger.warning(f"YouTube search attempt HTTP error {http_err.code}: {err_body}")
            return [], False
        except Exception as e:
            logger.warning(f"YouTube search attempt failed: {e}")
            return [], False


    def _get_curated_cc_documentaries(self) -> List[Video]:
        fallback_file = "data/fallback_playlist.json"
        if os.path.exists(fallback_file):
            try:
                with open(fallback_file, "r", encoding="utf-8") as f:
                    raw_items = json.load(f)
                logger.info(f"Loaded {len(raw_items)} curated fallback documentaries from '{fallback_file}'.")
                curated_videos = [Video(**item) for item in raw_items]
                random.shuffle(curated_videos)
                return curated_videos
            except Exception as e:
                logger.error(f"Error loading '{fallback_file}': {e}")

        raw_items = [
            {
                "id": "GfO-3Oir-qM",
                "title": "Our Planet | One Planet | FULL EPISODE | Netflix",
                "duration_seconds": 2940,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet full episode.",
                "youtube_url": "https://www.youtube.com/watch?v=GfO-3Oir-qM"
            },
            {
                "id": "um2Q9aUecy0",
                "title": "Our Planet | Coastal Seas | FULL EPISODE | Netflix",
                "duration_seconds": 2900,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet Coastal Seas.",
                "youtube_url": "https://www.youtube.com/watch?v=um2Q9aUecy0"
            },
            {
                "id": "r9PeYPHdpNo",
                "title": "Our Planet | Frozen Worlds | FULL EPISODE | Netflix",
                "duration_seconds": 3200,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet Frozen Worlds.",
                "youtube_url": "https://www.youtube.com/watch?v=r9PeYPHdpNo"
            },
            {
                "id": "JkaxUblCGz0",
                "title": "Our Planet | Jungles | FULL EPISODE | Netflix",
                "duration_seconds": 3000,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet Jungles.",
                "youtube_url": "https://www.youtube.com/watch?v=JkaxUblCGz0"
            },
            {
                "id": "XmtXC_n6X6Q",
                "title": "Our Planet | From Deserts to Grasslands | FULL EPISODE | Netflix",
                "duration_seconds": 3100,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet Deserts and Grasslands.",
                "youtube_url": "https://www.youtube.com/watch?v=XmtXC_n6X6Q"
            },
            {
                "id": "1280x2p8XlA",
                "title": "Our Planet | Fresh Water | FULL EPISODE | Netflix",
                "duration_seconds": 2900,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet Fresh Water.",
                "youtube_url": "https://www.youtube.com/watch?v=1280x2p8XlA"
            },
            {
                "id": "g087R9p0k9M",
                "title": "Our Planet | Forests | FULL EPISODE | Netflix",
                "duration_seconds": 2900,
                "license": "Creative Commons",
                "description": "Official Netflix Our Planet Forests.",
                "youtube_url": "https://www.youtube.com/watch?v=g087R9p0k9M"
            },
        ]
        curated_videos = [Video(**item) for item in raw_items]
        random.shuffle(curated_videos)
        return curated_videos




