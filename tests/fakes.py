"""
Test Fakes and Stubs for Clean Architecture Unit Testing.
Provides lightweight test doubles for ContentCollectorPort, StreamerPort, and TwitchPort.
"""

from typing import List, Optional, Set, Sequence, Union
from dokutv.domain.models import Video, PlayHistoryEntry
from dokutv.application.ports import (
    ContentCollectorPort,
    StreamerPort,
    TwitchPort,
    PlayHistoryPort,
)


class FakeContentCollectorAdapter(ContentCollectorPort):
    """Fake collector adapter for unit testing Use Cases without external HTTP calls."""

    def __init__(self, videos: Optional[List[Video]] = None):
        self.videos = videos or [
            Video(id="m1", title="Mock Doc 1", duration_seconds=3600, youtube_url="http://v1"),
            Video(id="m2", title="Mock Doc 2", duration_seconds=3600, youtube_url="http://v2"),
        ]

    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30) -> List[Video]:
        return list(self.videos)

    def get_next_video(
        self,
        query: str = "documentary",
        exclude_ids: Optional[Union[str, Set[str], Sequence[str]]] = None,
    ) -> Optional[Video]:
        exclude_set: Set[str] = set()
        if isinstance(exclude_ids, str):
            exclude_set = {exclude_ids}
        elif isinstance(exclude_ids, (set, list, tuple)):
            exclude_set = set(exclude_ids)

        for video in self.videos:
            if video.id not in exclude_set:
                return video
        return None


class FakeStreamerAdapter(StreamerPort):
    """Fake streamer adapter recording streaming invocations."""

    def __init__(self, success_response: bool = True):
        self.success_response = success_response
        self.streamed_sources: List[str] = []
        self.streamed_titles: List[str] = []

    def stream_video(
        self,
        input_source: str,
        video_title: str,
        duration_limit: Optional[int] = None,
        block: bool = True,
    ) -> bool:
        self.streamed_sources.append(input_source)
        self.streamed_titles.append(video_title)
        return self.success_response


class FakeTwitchAdapter(TwitchPort):
    """Fake Twitch adapter recording title updates."""

    def __init__(self, success_response: bool = True):
        self.success_response = success_response
        self.updated_titles: List[str] = []

    def update_stream_title(self, video_title: str) -> bool:
        self.updated_titles.append(video_title)
        return self.success_response


class FakeHistoryAdapter(PlayHistoryPort):
    """Fake play history adapter storing entries in memory."""

    def __init__(self) -> None:
        self.entries: List[PlayHistoryEntry] = []

    def add_entry(self, entry: PlayHistoryEntry) -> None:
        self.entries.append(entry)

    def get_history(self) -> List[PlayHistoryEntry]:
        return list(self.entries)

    def clear_history(self) -> None:
        self.entries.clear()

