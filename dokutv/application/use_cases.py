"""
Application Layer - Use Cases.
Contains application-specific business logic and orchestrates domain entities through ports.
Includes Pre-Fetching support for seamless continuous streaming.
"""

import logging
import threading
import time
from typing import Any, Optional, Tuple

from dokutv.domain.models import Video
from dokutv.application.ports import (
    ContentCollectorPort,
    StreamerPort,
    TwitchPort,
)

logger = logging.getLogger("ApplicationUseCases")


class StreamSingleVideoUseCase:
    """Use Case for selecting a video, updating Twitch, pre-fetching the next candidate, and streaming."""
    def __init__(
        self,
        collector_port: ContentCollectorPort,
        streamer_port: StreamerPort,
        twitch_port: TwitchPort,
    ):
        self.collector_port = collector_port
        self.streamer_port = streamer_port
        self.twitch_port = twitch_port
        self.next_pre_fetched_video: Optional[Video] = None

    def pre_fetch_next_video(self, query: str, exclude_ids: Optional[Any] = None) -> Optional[Video]:
        """Pre-fetch next video candidate in background before current video finishes."""
        try:
            logger.info(f"⚡ [Pre-Fetch] Fetching next candidate in background for query: '{query}'...")
            video = self.collector_port.get_next_video(query=query, exclude_ids=exclude_ids)
            if video:
                logger.info(f"⚡ [Pre-Fetch] Pre-fetched ready video: '{video.title}' (ID: {video.id})")
                self.next_pre_fetched_video = video
                return video
        except Exception as e:
            logger.warning(f"⚡ [Pre-Fetch] Failed to pre-fetch next video: {e}")
        return None

    def execute(
        self,
        query: str = "nature science documentary HD",
        exclude_ids: Optional[Any] = None,
        duration_limit: Optional[int] = None,
        current_video: Optional[Video] = None,
    ) -> Tuple[Optional[Video], Optional[Video]]:
        """
        Execute video streaming session.
        Returns tuple: (played_video, pre_fetched_next_video)
        """
        # 1. Use pre-fetched video if available, otherwise fetch new video
        video = current_video or self.next_pre_fetched_video or self.collector_port.get_next_video(query=query, exclude_ids=exclude_ids)
        self.next_pre_fetched_video = None

        if not video:
            logger.error("No video found to stream.")
            return None, None

        logger.info(f"Selected video for broadcast: '{video.title}' (ID: {video.id})")
        
        # 2. Update Twitch Title & Category
        self.twitch_port.update_stream_title(video.title)
        
        # 3. Schedule Pre-Fetch thread to load next video ~30s before end (or immediately if short duration)
        effective_duration = duration_limit or getattr(video, 'duration_seconds', 3600)
        prefetch_delay = max(1, effective_duration - 30)

        exclude_set = set(exclude_ids) if isinstance(exclude_ids, (set, list)) else set()
        exclude_set.add(video.id)

        prefetch_thread = threading.Thread(
            target=self.pre_fetch_next_video,
            args=(query, exclude_set),
            daemon=True
        )

        def delayed_prefetch():
            time.sleep(prefetch_delay)
            prefetch_thread.start()

        timer_thread = threading.Thread(target=delayed_prefetch, daemon=True)
        timer_thread.start()

        # 4. Stream video to Twitch (blocking until completed)
        video_source = video.youtube_url or "sample_doc.mp4"
        success = self.streamer_port.stream_video(
            video_source,
            video.title,
            duration_limit=duration_limit,
            block=True
        )

        if success:
            logger.info(f"Stream finished playing for '{video.title}'.")
            return video, self.next_pre_fetched_video
        else:
            logger.warning(f"Failed to stream '{video.title}' (ID: {video.id}). Blacklisting ID.")
            if isinstance(exclude_ids, set):
                exclude_ids.add(video.id)
            return None, None
