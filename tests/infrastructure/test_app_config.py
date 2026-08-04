import os
import unittest
from dokutv.infrastructure import AppConfig


class TestAppConfig(unittest.TestCase):

    def test_app_config_from_env(self):
        os.environ["TWITCH_CHANNEL_NAME"] = "TestChannel_EN"
        config = AppConfig.from_env()
        self.assertEqual(config.channel_name, "TestChannel_EN")


if __name__ == "__main__":
    unittest.main()
