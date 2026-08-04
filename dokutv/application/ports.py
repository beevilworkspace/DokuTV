"""
Application Layer - Ports (Interfaces / Protocols).
Defines abstract contracts for external dependencies using DIP.
"""

from typing import Protocol, List, Any, Optional
from dokutv.domain.models import Video


class ContentCollectorPort(Protocol):
    """Output Port for discovering documentary content."""
    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        ...
    def get_next_video(self, query: str = "documentary", exclude_ids: Optional[Any] = None) -> Optional[Video]:
        ...



class StreamerPort(Protocol):
    """Output Port for live video streaming."""
    def stream_video(self, input_source: str, video_title: str, duration_limit: Optional[int] = None, block: bool = True) -> bool:
        ...

class TwitchPort(Protocol):
    """Output Port for Twitch channel management."""
    def update_stream_title(self, video_title: str) -> bool:
        ...
