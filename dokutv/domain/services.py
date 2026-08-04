"""
Domain Services Package.
Contains domain services for stream title formatting and core business rules.
"""

from typing import Optional, Any


class TwitchTitleFormatter:
    """Formats raw video titles into Twitch broadcast stream titles."""

    def __init__(
        self,
        config: Optional[Any] = None,
        title_prefix: Optional[str] = None,
        title_suffix: Optional[str] = None,
    ):
        self.config = config
        self._title_prefix = title_prefix
        self._title_suffix = title_suffix

    @property
    def title_prefix(self) -> str:
        if self._title_prefix is not None:
            return self._title_prefix
        if self.config and hasattr(self.config, "title_prefix"):
            return getattr(self.config, "title_prefix")
        return ""

    @property
    def title_suffix(self) -> str:
        if self._title_suffix is not None:
            return self._title_suffix
        if self.config and hasattr(self.config, "title_suffix"):
            return getattr(self.config, "title_suffix")
        return ""

    def format_title(self, video_title: str) -> str:
        """Format stream title with standard prefix and suffix."""
        prefix = self.title_prefix
        suffix = self.title_suffix

        result = video_title
        if prefix:
            result = f"{prefix} {result}"
        if suffix:
            result = f"{result} {suffix}"

        return result.strip()


# Alias for Domain Service
TitleFormatter = TwitchTitleFormatter
