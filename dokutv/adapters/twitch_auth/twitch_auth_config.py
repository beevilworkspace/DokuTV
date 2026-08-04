"""
Configuration management for Twitch OAuth authorization.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class TwitchEndpoints:
    """Twitch OAuth endpoints."""
    authorize_url: str = "https://id.twitch.tv/oauth2/authorize"
    token_url: str = "https://id.twitch.tv/oauth2/token"


@dataclass
class TwitchAuthConfig:
    """Configuration for Twitch OAuth authentication flow."""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:3000/callback"
    scopes: str = "channel:manage:broadcast"
    token_file: Path = Path("data/twitch_tokens.json")
    endpoints: TwitchEndpoints = field(default_factory=TwitchEndpoints)

    @classmethod
    def from_env(
        cls,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_file: Optional[Path] = None,
    ) -> "TwitchAuthConfig":
        """Instantiate TwitchAuthConfig from environment variables and parameters."""
        c_id = client_id or os.getenv("TWITCH_CLIENT_ID", "")
        c_secret = client_secret or os.getenv("TWITCH_CLIENT_SECRET", "")
        path = token_file or Path(os.getenv("TWITCH_TOKEN_FILE", "data/twitch_tokens.json"))
        return cls(
            client_id=c_id,
            client_secret=c_secret,
            token_file=path,
        )
