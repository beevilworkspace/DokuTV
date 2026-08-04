"""
DokuTV Clean Architecture Package Root
"""

from dokutv.engine import DokuTVEngine
from dokutv.domain import Video, PlaySlot, ChannelSchedule
from dokutv.application import (
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

__all__ = [
    "DokuTVEngine",
    "Video",
    "PlaySlot",
    "ChannelSchedule",
    "DiscoverContentUseCase",
    "PlanScheduleUseCase",
    "StreamCurrentSlotUseCase",
    "YouTubeCollectorAdapter",
    "ScheduleRepositoryAdapter",
    "FFmpegStreamerAdapter",
    "TwitchHelixAdapter",
]
