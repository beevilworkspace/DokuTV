"""
Streaming target abstraction for RTMP endpoints.
Decouples Twitch-specific URLs from the core streaming logic.
"""

from abc import ABC, abstractmethod
from typing import Optional


class StreamingTarget(ABC):
    """Abstract base for streaming destination targets."""

    @abstractmethod
    def get_rtmp_url(self, stream_key: Optional[str] = None) -> str:
        """Construct full RTMP URL including stream key."""
        pass


class TwitchTarget(StreamingTarget):
    """Twitch RTMP streaming target."""

    DEFAULT_BASE_URL = "rtmp://live.twitch.tv/app"

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or self.DEFAULT_BASE_URL

    def get_rtmp_url(self, stream_key: Optional[str] = None) -> str:
        key = stream_key or ""
        return f"{self.base_url}/{key}".rstrip("/")


class CustomRtmpTarget(StreamingTarget):
    """Generic RTMP streaming target for YouTube Live, Kick, Nginx RTMP, etc."""

    def __init__(self, rtmp_url: str):
        self.rtmp_url = rtmp_url

    def get_rtmp_url(self, stream_key: Optional[str] = None) -> str:
        if stream_key and not self.rtmp_url.endswith(stream_key):
            return f"{self.rtmp_url.rstrip('/')}/{stream_key}"
        return self.rtmp_url
