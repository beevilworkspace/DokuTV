"""
Application Layer - Streamer Ports.
Defines abstract contracts for live video streaming using DIP.
"""

from typing import Protocol, Optional, runtime_checkable


@runtime_checkable
class StreamerPort(Protocol):
    """Output Port for live video streaming."""

    def stream_video(
        self,
        input_source: str,
        video_title: str,
        duration_limit: Optional[int] = None,
        block: bool = True,
    ) -> bool:
        """Stream a video source to broadcast target."""
        ...


@runtime_checkable
class PersistentStreamerPort(StreamerPort, Protocol):
    """Output Port extending StreamerPort with continuous persistent stream lifecycle management."""

    def start_persistent_stream(self) -> bool:
        """Start a persistent continuous broadcast process."""
        ...

    def stop_persistent_stream(self) -> None:
        """Gracefully stop persistent broadcast process."""
        ...
