"""
Configuration management for streaming operations.
Centralizes environment variable lookups and default FFmpeg parameters.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StreamingConfig:
    """Configuration options for FFmpeg streaming and URL resolving."""
    video_preset: str = "veryfast"
    video_maxrate: str = "6000k"
    buffer_size: str = "12000k"
    audio_bitrate: str = "160k"
    audio_sample_rate: str = "44100"
    pixel_format: str = "yuv420p"
    gop_size: int = 120

    quality_preference: List[str] = field(default_factory=lambda: [
        "best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"
    ])

    youtube_cookies_file: Optional[str] = None
    youtube_cookies_browser: Optional[str] = None

    @classmethod
    def from_env(cls) -> "StreamingConfig":
        """Instantiate config with settings populated from environment variables."""
        cookies_file = os.getenv("YOUTUBE_COOKIES_FILE") or (
            "cookies.txt" if os.path.exists("cookies.txt") else None
        )
        cookies_browser = os.getenv("YOUTUBE_COOKIES_BROWSER")
        return cls(
            youtube_cookies_file=cookies_file,
            youtube_cookies_browser=cookies_browser,
        )
