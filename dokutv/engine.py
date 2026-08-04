"""
Composition Root - DokuTV Engine.
Assembles Adapters and Use Cases into a unified high-level engine.
"""

import logging
from typing import Dict, Any, List, Optional

from dokutv.domain.models import Video, PlaySlot
from dokutv.domain.topics import get_random_topic
from dokutv.application.use_cases import (
    DiscoverContentUseCase,
    PlanScheduleUseCase,
    StreamCurrentSlotUseCase,
)
from dokutv.adapters import (
    YouTubeCollectorAdapter,
    ScheduleRepositoryAdapter,
    FFmpegStreamerAdapter,
    TwitchHelixAdapter,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DokuTVEngine")

class DokuTVEngine:
    def __init__(self, channel_name: str = "DokuTV_EN", dry_run: bool = False):
        self.channel_name = channel_name
        self.dry_run = dry_run

        # 1. Instantiate Adapters (Layer 3)
        self.collector_adapter = YouTubeCollectorAdapter()
        self.schedule_repo_adapter = ScheduleRepositoryAdapter(playlist_file="data/playlist_cache.json")
        self.streamer_adapter = FFmpegStreamerAdapter()
        self.twitch_adapter = TwitchHelixAdapter(channel_name=self.channel_name)

        # 2. Inject Adapters into Use Cases (Layer 2)
        self.discover_use_case = DiscoverContentUseCase(collector_port=self.collector_adapter)
        self.plan_schedule_use_case = PlanScheduleUseCase(schedule_repo_port=self.schedule_repo_adapter)
        self.stream_slot_use_case = StreamCurrentSlotUseCase(
            schedule_repo_port=self.schedule_repo_adapter,
            streamer_port=self.streamer_adapter,
            twitch_port=self.twitch_adapter,
        )

        self.videos: List[Video] = []
        self.schedule: List[PlaySlot] = []
        self.is_running = False

    def initialize(self, query: Optional[str] = None) -> Dict[str, Any]:
        selected_query = query or get_random_topic()
        logger.info(f"DokuTVEngine Composition Root: Initializing with topic: '{selected_query}'...")
        self.videos = self.discover_use_case.execute(query=selected_query, max_results=30)
        self.schedule = self.plan_schedule_use_case.execute(videos=self.videos)

        logger.info(f"Initialized with {len(self.schedule)} schedule slots.")
        return {
            "status": "initialized",
            "video_count": len(self.videos),
            "slots_count": len(self.schedule),
        }

    def start(self) -> Dict[str, Any]:
        if not self.schedule:
            self.initialize()

        self.is_running = True
        result = self.stream_slot_use_case.execute(self.schedule)
        
        return {
            "is_running": self.is_running,
            "current_slot": result["current_slot"],
            "stream_launched": result["stream_launched"],
        }

    def get_status(self) -> Dict[str, Any]:
        current_slot = (
            self.schedule_repo_adapter.get_current_playing_slot(self.schedule)
            if self.schedule else None
        )
        return {
            "channel_name": self.channel_name,
            "is_running": self.is_running,
            "dry_run": self.dry_run,
            "current_slot": current_slot.__dict__ if current_slot else None,
            "streamer_key_set": bool(self.streamer_adapter.stream_key),
        }

    def stop(self) -> None:
        logger.info("Stopping DokuTVEngine operations.")
        self.is_running = False
