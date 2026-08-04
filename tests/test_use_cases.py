import unittest
from dokutv.domain.models import Video
from dokutv.application.use_cases import (
    StreamSingleVideoUseCase,
)

class MockCollectorAdapter:
    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30):
        return [Video(id="m1", title="Mock Doc 1"), Video(id="m2", title="Mock Doc 2")]
    def get_next_video(self, query: str = "documentary", exclude_ids=None):
        if exclude_ids and "m1" in exclude_ids:
            return Video(id="m2", title="Mock Doc 2")
        return Video(id="m1", title="Mock Doc 1")


class MockStreamer:
    def __init__(self):
        self.streamed_titles = []

    def stream_video(self, video_source: str, title: str, duration_limit=None, block=True) -> bool:
        self.streamed_titles.append(title)
        return True

class MockTwitchAdapter:
    def __init__(self):
        self.updated_title = None

    def update_stream_title(self, title: str) -> bool:
        self.updated_title = title
        return True

class TestUseCases(unittest.TestCase):
    def test_stream_single_video_use_case(self):
        collector = MockCollectorAdapter()
        streamer = MockStreamer()
        twitch = MockTwitchAdapter()

        use_case = StreamSingleVideoUseCase(
            collector_port=collector,
            streamer_port=streamer,
            twitch_port=twitch,
        )

        video, _ = use_case.execute(exclude_ids={"m1"})

        self.assertIsNotNone(video)
        self.assertEqual(video.id, "m2")
        self.assertEqual(video.title, "Mock Doc 2")
        self.assertEqual(streamer.streamed_titles, ["Mock Doc 2"])
        self.assertEqual(twitch.updated_title, "Mock Doc 2")

if __name__ == "__main__":
    unittest.main()
