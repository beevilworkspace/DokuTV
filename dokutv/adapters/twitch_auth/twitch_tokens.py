"""
Twitch OAuth token data model.
Encapsulates token attributes and expiration logic.
"""

import time
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TwitchTokens:
    """Represents Twitch User OAuth access and refresh tokens."""
    access_token: str
    refresh_token: str
    expires_at: float

    def is_expired(self, buffer_seconds: float = 60.0) -> bool:
        """Check if access token is expired or within buffer period."""
        return time.time() >= (self.expires_at - buffer_seconds)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tokens to dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TwitchTokens":
        """Deserialize tokens from dictionary."""
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=float(data.get("expires_at", 0.0)),
        )
