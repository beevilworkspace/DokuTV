import unittest
from dokutv.adapters import FFmpegStreamerAdapter

class TestFFmpegStreamerAdapter(unittest.TestCase):
    def test_dry_run_streaming(self):
        engine = FFmpegStreamerAdapter(stream_key="live_123456789_placeholder")
        result = engine.stream_video("https://www.youtube.com/watch?v=21X5lGlDOfg", "Test Title")
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
