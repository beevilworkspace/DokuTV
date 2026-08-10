"""
Infrastructure Layer - Application Configuration.
Centralized dataclass for application-wide environment configuration.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Global infrastructure configuration for DokuTV application."""
    youtube_api_key: str = ""
    twitch_client_id: str = ""
    twitch_client_secret: str = ""
    twitch_stream_key: str = ""
    channel_name: str = "DokuTV_EN"
    dry_run: bool = False
    history_file_path: str = "data/history.json"

    @classmethod
    def from_env(
        cls,
        channel_name: Optional[str] = None,
        dry_run: Optional[bool] = None,
        history_file_path: Optional[str] = None,
    ) -> "AppConfig":
        """Load global application configuration from environment variables."""
        key_yt = os.getenv("YOUTUBE_API_KEY", "")
        client_id = os.getenv("TWITCH_CLIENT_ID", "")
        client_secret = os.getenv("TWITCH_CLIENT_SECRET", "")
        stream_key = os.getenv("TWITCH_STREAM_KEY", "")
        c_name = channel_name or os.getenv("TWITCH_CHANNEL_NAME", "DokuTV_EN")
        is_dry = dry_run if dry_run is not None else os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
        h_path = history_file_path or os.getenv("HISTORY_FILE_PATH", "data/history.json")

        return cls(
            youtube_api_key=key_yt,
            twitch_client_id=client_id,
            twitch_client_secret=client_secret,
            twitch_stream_key=stream_key,
            channel_name=c_name,
            dry_run=is_dry,
            history_file_path=h_path,
        )

