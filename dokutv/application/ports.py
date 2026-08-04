"""
Application Layer - Ports (Interfaces / Protocols).
Defines abstract contracts for external dependencies using DIP.
"""

from typing import Protocol, List, Dict, Any, Optional
from dokutv.domain.models import Video, PlaySlot

class ContentCollectorPort(Protocol):
    """Output Port for discovering documentary content."""
    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        ...
    def save_playlist_cache(self, videos: List[Video], filepath: str = "data/playlist_cache.json") -> None:
        ...

class ScheduleRepositoryPort(Protocol):
    """Output Port for managing and persisting schedules."""
    def load_videos(self) -> List[Video]:
        ...
    def generate_30_day_schedule(self, videos: List[Video]) -> List[PlaySlot]:
        ...
    def get_current_playing_slot(self, schedule: List[PlaySlot]) -> Optional[PlaySlot]:
        ...
    def save_schedule(self, schedule: List[PlaySlot], filepath: str = "data/schedule_30_days.json") -> None:
        ...

class StreamerPort(Protocol):
    """Output Port for live video streaming."""
    def stream_video(self, input_source: str, video_title: str) -> bool:
        ...

class TwitchPort(Protocol):
    """Output Port for Twitch channel management."""
    def update_stream_title(self, video_title: str) -> bool:
        ...
