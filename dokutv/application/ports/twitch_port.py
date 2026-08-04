"""
Application Layer - Twitch Channel Management Ports.
Defines abstract contracts for live broadcast channel management using DIP.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class TwitchPort(Protocol):
    """Output Port for Twitch channel management."""

    def update_stream_title(self, video_title: str) -> bool:
        """Update active channel broadcast title and category."""
        ...


# Interface Alias for platform-agnostic channel management
ChannelManagementPort = TwitchPort
