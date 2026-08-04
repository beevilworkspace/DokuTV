"""
Configuration management for Twitch Helix API operations.
Centralizes environment variable lookups and default Twitch API parameters.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TwitchEndpoints:
    """Twitch API endpoints."""
    token_url: str = "https://id.twitch.tv/oauth2/token"
    users_url: str = "https://api.twitch.tv/helix/users"
    channels_url: str = "https://api.twitch.tv/helix/channels"


@dataclass
class TwitchHelixConfig:
    """Configuration options for Twitch Helix API operations."""
    channel_name: str = "DokuTV_EN"
    client_id: str = ""
    client_secret: str = ""
    default_category_id: str = "509658"  # "Just Chatting"
    title_prefix: str = "🔴 24/7 Doku:"
    title_suffix: str = "| DokuTV_EN"
    endpoints: TwitchEndpoints = field(default_factory=TwitchEndpoints)

    @classmethod
    def from_env(
        cls,
        channel_name: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> "TwitchHelixConfig":
        """Instantiate config with settings populated from environment variables."""
        c_name = channel_name or os.getenv("TWITCH_CHANNEL_NAME", "DokuTV_EN")
        c_id = client_id or os.getenv("TWITCH_CLIENT_ID", "")
        c_secret = client_secret or os.getenv("TWITCH_CLIENT_SECRET", "")
        return cls(
            channel_name=c_name,
            client_id=c_id,
            client_secret=c_secret,
        )
