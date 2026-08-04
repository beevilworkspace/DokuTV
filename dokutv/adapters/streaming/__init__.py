"""
Streaming subpackage for FFmpeg live streaming adapter components.
"""

from dokutv.adapters.streaming.models import StreamResult, ResolvedStream
from dokutv.adapters.streaming.config import StreamingConfig
from dokutv.adapters.streaming.target import StreamingTarget, TwitchTarget, CustomRtmpTarget
from dokutv.adapters.streaming.locator import FFmpegBinaryLocator
from dokutv.adapters.streaming.cookies import CookieProvider
from dokutv.adapters.streaming.resolver import YoutubeUrlResolver
from dokutv.adapters.streaming.command_builder import FFmpegCommandBuilder
from dokutv.adapters.streaming.session import PersistentStreamSession

__all__ = [
    "StreamResult",
    "ResolvedStream",
    "StreamingConfig",
    "StreamingTarget",
    "TwitchTarget",
    "CustomRtmpTarget",
    "FFmpegBinaryLocator",
    "CookieProvider",
    "YoutubeUrlResolver",
    "FFmpegCommandBuilder",
    "PersistentStreamSession",
]
