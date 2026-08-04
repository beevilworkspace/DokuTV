"""
Application Layer - Use Cases.
Contains application-specific business logic and orchestrates domain entities through ports.
"""

import logging
from typing import List, Dict, Any, Optional

from dokutv.domain.models import Video, PlaySlot
from dokutv.application.ports import (
    ContentCollectorPort,
    ScheduleRepositoryPort,
    StreamerPort,
    TwitchPort,
)

logger = logging.getLogger("ApplicationUseCases")

class DiscoverContentUseCase:
    """Use Case for searching documentaries and saving cache."""
    def __init__(self, collector_port: ContentCollectorPort):
        self.collector_port = collector_port

    def execute(self, query: str = "nature science documentary HD", max_results: int = 30) -> List[Video]:
        logger.info(f"DiscoverContentUseCase: Executing discovery for '{query}'...")
        videos = self.collector_port.search_cc_documentaries(query=query, max_results=max_results)
        self.collector_port.save_playlist_cache(videos)
        return videos

class PlanScheduleUseCase:
    """Use Case for generating 30-day broadcast schedule."""
    def __init__(self, schedule_repo_port: ScheduleRepositoryPort):
        self.schedule_repo_port = schedule_repo_port

    def execute(self, videos: Optional[List[Video]] = None) -> List[PlaySlot]:
        logger.info("PlanScheduleUseCase: Generating 30-day schedule...")
        if not videos:
            videos = self.schedule_repo_port.load_videos()
        schedule = self.schedule_repo_port.generate_30_day_schedule(videos)
        self.schedule_repo_port.save_schedule(schedule)
        return schedule

class StreamCurrentSlotUseCase:
    """Use Case for playing the active schedule slot and updating Twitch title."""
    def __init__(
        self,
        schedule_repo_port: ScheduleRepositoryPort,
        streamer_port: StreamerPort,
        twitch_port: TwitchPort,
    ):
        self.schedule_repo_port = schedule_repo_port
        self.streamer_port = streamer_port
        self.twitch_port = twitch_port

    def execute(self, schedule: List[PlaySlot], max_retries: int = 5) -> Dict[str, Any]:
        logger.info("StreamCurrentSlotUseCase: Determining active play slot...")
        current_slot = self.schedule_repo_port.get_current_playing_slot(schedule)
        if not current_slot:
            raise ValueError("No playing slot available in schedule.")

        start_idx = current_slot.slot_index - 1
        for offset in range(min(max_retries, len(schedule))):
            candidate_slot = schedule[(start_idx + offset) % len(schedule)]
            logger.info(f"StreamCurrentSlotUseCase: Attempting slot #{candidate_slot.slot_index} - '{candidate_slot.title}'")
            
            video_source = candidate_slot.youtube_url or "sample_doc.mp4"
            success = self.streamer_port.stream_video(video_source, candidate_slot.title)

            if success:
                self.twitch_port.update_stream_title(candidate_slot.title)
                return {
                    "current_slot": candidate_slot,
                    "stream_launched": True,
                }
            
            logger.warning(f"Slot #{candidate_slot.slot_index} ('{candidate_slot.title}') is unplayable. Retrying with next slot...")

        return {
            "current_slot": current_slot,
            "stream_launched": False,
        }
