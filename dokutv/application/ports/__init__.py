"""
Application Layer Ports Subpackage.
Defines abstract contracts for external dependencies using Dependency Inversion Principle (DIP).
"""

from dokutv.application.ports.collector_port import ContentCollectorPort
from dokutv.application.ports.streamer_port import StreamerPort, PersistentStreamerPort
from dokutv.application.ports.twitch_port import TwitchPort, ChannelManagementPort
from dokutv.application.ports.history_port import PlayHistoryPort

__all__ = [
    "ContentCollectorPort",
    "StreamerPort",
    "PersistentStreamerPort",
    "TwitchPort",
    "ChannelManagementPort",
    "PlayHistoryPort",
]

