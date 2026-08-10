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
    video_maxrate: str = "4500k"
    buffer_size: str = "9000k"
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
        maxrate = os.getenv("VIDEO_MAXRATE", "4500k")
        bufsize = os.getenv("BUFFER_SIZE", "9000k")
        preset = os.getenv("VIDEO_PRESET", "veryfast")

        return cls(
            video_preset=preset,
            video_maxrate=maxrate,
            buffer_size=bufsize,
            youtube_cookies_file=cookies_file,
            youtube_cookies_browser=cookies_browser,
        )

