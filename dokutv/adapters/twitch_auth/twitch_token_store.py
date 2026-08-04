"""
Persistence component for Twitch User OAuth tokens.
Manages file I/O operations for tokens.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from dokutv.adapters.twitch_auth.twitch_tokens import TwitchTokens

logger = logging.getLogger(__name__)


class TwitchTokenStore:
    """Manages reading, writing, and clearing Twitch tokens on disk."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def exists(self) -> bool:
        """Check if token file exists."""
        return self.file_path.exists()

    def load(self) -> Optional[TwitchTokens]:
        """Load tokens from file if available."""
        if not self.file_path.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded saved Twitch User OAuth tokens from {self.file_path}.")
            return TwitchTokens.from_dict(data)
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"Failed to load tokens from {self.file_path}: {e}")
            return None

    def save(self, tokens: TwitchTokens) -> None:
        """Save tokens to disk."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(tokens.to_dict(), f, indent=2)
            logger.info(f"Twitch User OAuth tokens saved to {self.file_path}.")
        except OSError as e:
            logger.error(f"Failed to save tokens to {self.file_path}: {e}")

    def clear(self) -> None:
        """Delete stored tokens from disk."""
        if self.file_path.exists():
            try:
                self.file_path.unlink()
                logger.info(f"Cleared tokens file {self.file_path}.")
            except OSError as e:
                logger.error(f"Failed to delete token file {self.file_path}: {e}")
