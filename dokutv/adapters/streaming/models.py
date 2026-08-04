"""
Models and data transfer objects for streaming operations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResolvedStream:
    """Represents a resolved media stream with single or dual (video/audio) URLs."""
    video_url: str
    audio_url: Optional[str] = None
    resolution: str = "1080p"
    is_dual_input: bool = False

    @property
    def is_valid(self) -> bool:
        return bool(self.video_url)


@dataclass
class StreamResult:
    """Detailed result status for video streaming operations."""
    success: bool
    error: Optional[str] = None
    duration: Optional[float] = None
    resolved_url: Optional[str] = None
    resolved_stream: Optional[ResolvedStream] = None
    exit_code: Optional[int] = None
