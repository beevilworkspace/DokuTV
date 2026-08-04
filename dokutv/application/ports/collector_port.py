"""
Application Layer - Content Collector Port.
Defines abstract contracts for documentary content discovery using DIP.
"""

from typing import Protocol, List, Optional, Set, Sequence, Union, runtime_checkable
from dokutv.domain.models import Video


@runtime_checkable
class ContentCollectorPort(Protocol):
    """Output Port for discovering documentary content."""

    def search_cc_documentaries(
        self,
        query: str = "documentary",
        max_results: int = 30,
    ) -> List[Video]:
        """Search Creative Commons documentary videos."""
        ...

    def get_next_video(
        self,
        query: str = "documentary",
        exclude_ids: Optional[Union[str, Set[str], Sequence[str]]] = None,
    ) -> Optional[Video]:
        """Select next video candidate whose ID is not excluded."""
        ...
