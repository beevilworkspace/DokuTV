import unittest
from dokutv.domain import Video
from dokutv.application import StreamSingleVideoUseCase
from tests.fakes import (
    FakeContentCollectorAdapter,
    FakeStreamerAdapter,
    FakeTwitchAdapter,
)


class TestStreamSingleVideoUseCase(unittest.TestCase):

    def test_stream_single_video_execution(self):
        collector = FakeContentCollectorAdapter()
        streamer = FakeStreamerAdapter()
        twitch = FakeTwitchAdapter()

        use_case = StreamSingleVideoUseCase(
            collector_port=collector,
            streamer_port=streamer,
            twitch_port=twitch,
        )

        video, _ = use_case.execute(query="nature", exclude_ids={"m1"})

        self.assertIsNotNone(video)
        self.assertEqual(video.id, "m2")
        self.assertEqual(video.title, "Mock Doc 2")
        self.assertEqual(streamer.streamed_titles, ["Mock Doc 2"])
        self.assertEqual(twitch.updated_titles, ["Mock Doc 2"])


if __name__ == "__main__":
    unittest.main()
