import unittest
from dokutv.engine import DokuTVEngine

class TestDokuTVCleanEngine(unittest.TestCase):
    def test_clean_architecture_engine_lifecycle(self):
        engine = DokuTVEngine(channel_name="DokuTV_EN", dry_run=True)
        init_res = engine.initialize(query="nature")
        self.assertEqual(init_res["status"], "initialized")
        self.assertGreater(init_res["video_count"], 0)

        run_res = engine.start()
        self.assertTrue(run_res["is_running"])
        self.assertTrue(run_res["stream_launched"])

        status = engine.get_status()
        self.assertEqual(status["channel_name"], "DokuTV_EN")
        self.assertTrue(status["is_running"])

        engine.stop()
        self.assertFalse(engine.is_running)

if __name__ == "__main__":
    unittest.main()
