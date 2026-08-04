"""
DokuTV Clean Architecture Package Root
"""

from dokutv.engine import DokuTVEngine
from dokutv.domain import Video, PlaySlot, ChannelSchedule
from dokutv.application import (
    StreamSingleVideoUseCase,
)
from dokutv.adapters import (
    YouTubeCollectorAdapter,
    FFmpegStreamerAdapter,
    TwitchHelixAdapter,
)

__all__ = [
    "DokuTVEngine",
    "Video",
    "PlaySlot",
    "ChannelSchedule",
    "StreamSingleVideoUseCase",
    "YouTubeCollectorAdapter",
    "FFmpegStreamerAdapter",
    "TwitchHelixAdapter",
]
