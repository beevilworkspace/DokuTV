import unittest
from dokutv.engine import DokuTVEngine

class TestDokuTVCleanEngine(unittest.TestCase):
    def test_clean_architecture_engine_lifecycle(self):
        engine = DokuTVEngine(channel_name="DokuTV_EN", dry_run=True)
        
        status = engine.get_status()
        self.assertEqual(status["channel_name"], "DokuTV_EN")
        self.assertFalse(status["is_running"])
        self.assertTrue(status["dry_run"])

        engine.stop()
        self.assertFalse(engine.is_running)

if __name__ == "__main__":
    unittest.main()
