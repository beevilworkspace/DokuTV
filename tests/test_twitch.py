import unittest
from dokutv.adapters import TwitchHelixAdapter

class TestTwitchHelixAdapter(unittest.TestCase):
    def test_dry_run_title_update(self):
        bot = TwitchHelixAdapter(channel_name="DokuTV_EN")
        res = bot.update_stream_title("Apollo 11 Moon Landing")
        self.assertTrue(res)

if __name__ == "__main__":
    unittest.main()
