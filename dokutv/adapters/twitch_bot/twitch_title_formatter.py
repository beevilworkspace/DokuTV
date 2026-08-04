"""
Title formatter component for Twitch stream titles.
Encapsulates formatting logic and prefix/suffix handling.
"""

from dokutv.adapters.twitch_bot.twitch_helix_config import TwitchHelixConfig


class TwitchTitleFormatter:
    """Formats raw video titles into Twitch broadcast stream titles."""

    def __init__(self, config: TwitchHelixConfig):
        self.config = config

    def format_title(self, video_title: str) -> str:
        """Format stream title with standard prefix and suffix."""
        return f"{self.config.title_prefix} {video_title} {self.config.title_suffix}"
