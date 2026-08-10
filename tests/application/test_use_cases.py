import unittest
from dokutv.domain import Video
from dokutv.application import StreamSingleVideoUseCase
from tests.fakes import (
    FakeContentCollectorAdapter,
    FakeStreamerAdapter,
    FakeTwitchAdapter,
    FakeHistoryAdapter,
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

    def test_stream_single_video_history_recording(self):
        collector = FakeContentCollectorAdapter()
        streamer = FakeStreamerAdapter(success_response=True)
        twitch = FakeTwitchAdapter()
        history = FakeHistoryAdapter()

        use_case = StreamSingleVideoUseCase(
            collector_port=collector,
            streamer_port=streamer,
            twitch_port=twitch,
            history_port=history,
        )

        video, _ = use_case.execute(query="space", exclude_ids=set())

        self.assertIsNotNone(video)
        self.assertEqual(len(history.entries), 1)
        entry = history.entries[0]
        self.assertEqual(entry.video_id, "m1")
        self.assertEqual(entry.title, "Mock Doc 1")
        self.assertEqual(entry.topic, "space")
        self.assertEqual(entry.status, "played")

    def test_stream_single_video_history_failure_recording(self):
        collector = FakeContentCollectorAdapter()
        streamer = FakeStreamerAdapter(success_response=False)
        twitch = FakeTwitchAdapter()
        history = FakeHistoryAdapter()

        use_case = StreamSingleVideoUseCase(
            collector_port=collector,
            streamer_port=streamer,
            twitch_port=twitch,
            history_port=history,
        )

        video, _ = use_case.execute(query="space", exclude_ids=set())

        self.assertIsNone(video)
        self.assertEqual(len(history.entries), 1)
        entry = history.entries[0]
        self.assertEqual(entry.video_id, "m1")



if __name__ == "__main__":
    unittest.main()

