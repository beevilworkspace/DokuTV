import unittest
from dokutv.adapters import (
    FFmpegStreamerAdapter,
    StreamingConfig,
    TwitchTarget,
    CustomRtmpTarget,
    FFmpegCommandBuilder,
    PersistentStreamSession,
    YoutubeUrlResolver,
)


class TestFFmpegStreamerAdapter(unittest.TestCase):

    def test_dry_run_streaming(self):
        engine = FFmpegStreamerAdapter(stream_key="live_123456789_placeholder")
        self.assertTrue(engine.is_simulation)
        result = engine.stream_video("sample_video.mp4", "Test Title")
        self.assertTrue(result)

    def test_streaming_config_defaults(self):
        config = StreamingConfig()
        self.assertEqual(config.video_preset, "veryfast")
        self.assertEqual(config.video_maxrate, "6000k")
        self.assertEqual(config.audio_bitrate, "160k")

    def test_streaming_targets(self):
        twitch_target = TwitchTarget()
        self.assertEqual(
            twitch_target.get_rtmp_url("my_secret_key"),
            "rtmp://live.twitch.tv/app/my_secret_key"
        )

        custom_target = CustomRtmpTarget("rtmp://a.rtmp.youtube.com/live2")
        self.assertEqual(
            custom_target.get_rtmp_url("yt_key"),
            "rtmp://a.rtmp.youtube.com/live2/yt_key"
        )

    def test_command_builder(self):
        config = StreamingConfig(video_preset="fast", video_maxrate="4000k")
        builder = FFmpegCommandBuilder(config=config)

        cmd_feeder = builder.build_feeder_command("ffmpeg", "input.mp4", duration_limit=30)
        self.assertIn("-preset", cmd_feeder)
        self.assertIn("fast", cmd_feeder)
        self.assertIn("-t", cmd_feeder)
        self.assertIn("30", cmd_feeder)

        cmd_rtmp = builder.build_persistent_rtmp_command("ffmpeg", "rtmp://live.twitch.tv/app/key")
        self.assertEqual(cmd_rtmp[0], "ffmpeg")
        self.assertIn("mpegts", cmd_rtmp)
        self.assertEqual(cmd_rtmp[-1], "rtmp://live.twitch.tv/app/key")

    def test_persistent_stream_session_initial_state(self):
        session = PersistentStreamSession()
        self.assertFalse(session.is_alive)
        self.assertIsNone(session.process)

    def test_youtube_url_resolver_non_http(self):
        resolver = YoutubeUrlResolver()
        local_path = "C:/media/sample.mp4"
        self.assertEqual(resolver.resolve(local_path), local_path)


if __name__ == "__main__":
    unittest.main()
