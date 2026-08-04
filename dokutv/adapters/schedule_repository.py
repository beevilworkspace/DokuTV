"""
Interface Adapters - Schedule Repository Adapter.
Implements ScheduleRepositoryPort.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from dokutv.domain.models import Video, PlaySlot
from dokutv.application.ports import ScheduleRepositoryPort

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ScheduleRepositoryAdapter")

class ScheduleRepositoryAdapter(ScheduleRepositoryPort):
    def __init__(self, playlist_file: str = "data/playlist_cache.json"):
        self.playlist_file = playlist_file

    def load_videos(self) -> List[Video]:
        if os.path.exists(self.playlist_file):
            with open(self.playlist_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} videos from '{self.playlist_file}'.")
            return [Video(**v) for v in data]
        
        logger.warning(f"Playlist file '{self.playlist_file}' not found. Generating default video list.")
        return [
            Video(
                id=f"doc_{i:03d}",
                title=f"Documentary {i:03d}",
                duration_seconds=3600,
                youtube_url=f"https://www.youtube.com/watch?v=doc_{i:03d}"
            )
            for i in range(1, 721)
        ]

    def generate_30_day_schedule(self, videos: List[Video], start_time: Optional[datetime] = None) -> List[PlaySlot]:
        if not videos:
            videos = self.load_videos()

        start_time = start_time or datetime.now()
        current_time = start_time
        schedule: List[PlaySlot] = []

        video_idx = 0
        target_end_time = start_time + timedelta(days=30)

        while current_time < target_end_time:
            video = videos[video_idx % len(videos)]
            duration = timedelta(seconds=video.duration_seconds)
            
            slot = PlaySlot(
                slot_index=len(schedule) + 1,
                video_id=video.id,
                title=video.title,
                youtube_url=video.youtube_url,
                start_time=current_time.isoformat(),
                end_time=(current_time + duration).isoformat(),
                duration_seconds=video.duration_seconds
            )
            schedule.append(slot)
            current_time += duration
            video_idx += 1

        logger.info(f"Generated 30-day schedule with {len(schedule)} slots.")
        return schedule

    def get_current_playing_slot(self, schedule: List[PlaySlot], now: Optional[datetime] = None) -> Optional[PlaySlot]:
        now = now or datetime.now()
        if not schedule:
            return None

        schedule_start = datetime.fromisoformat(schedule[0].start_time)
        total_cycle_seconds = (datetime.fromisoformat(schedule[-1].end_time) - schedule_start).total_seconds()
        
        elapsed_seconds = (now - schedule_start).total_seconds() % total_cycle_seconds

        accumulated = 0.0
        for slot in schedule:
            accumulated += slot.duration_seconds
            if elapsed_seconds < accumulated:
                return slot
        return schedule[0]

    def save_schedule(self, schedule: List[PlaySlot], filepath: str = "data/schedule_30_days.json") -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        raw_list = [s.__dict__ for s in schedule]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(raw_list, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(schedule)} schedule slots to '{filepath}'.")
