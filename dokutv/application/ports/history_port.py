"""
Application Layer - Play History Port.
Defines abstract contracts for recording and querying broadcast video history using DIP.
"""

from typing import Protocol, List, runtime_checkable
from dokutv.domain.models import PlayHistoryEntry


@runtime_checkable
class PlayHistoryPort(Protocol):
    """Output Port for persisting and retrieving broadcast history."""

    def add_entry(self, entry: PlayHistoryEntry) -> None:
        """Add a video play history entry."""
        ...

    def get_history(self) -> List[PlayHistoryEntry]:
        """Retrieve all recorded play history entries."""
        ...

    def clear_history(self) -> None:
        """Clear recorded play history."""
        ...
