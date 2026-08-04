import unittest
from unittest.mock import MagicMock

from dokutv.adapters.twitch_bot import (
    TwitchHelixConfig,
    TwitchTitleFormatter,
    TwitchHelixAdapter,
)
from dokutv.adapters.twitch_auth import TwitchAuthManager


class TestTwitchBotAdapter(unittest.TestCase):

    def test_title_formatter(self):
        config = TwitchHelixConfig(
            title_prefix="🔴 24/7 Doku:",
            title_suffix="| DokuTV_EN",
        )
        formatter = TwitchTitleFormatter(config)
        formatted = formatter.format_title("Wonders of the Universe")
        self.assertEqual(formatted, "🔴 24/7 Doku: Wonders of the Universe | DokuTV_EN")

    def test_helix_config_defaults(self):
        config = TwitchHelixConfig()
        self.assertEqual(config.default_category_id, "509658")
        self.assertEqual(config.channel_name, "DokuTV_EN")

    def test_helix_adapter_dry_run(self):
        config = TwitchHelixConfig(channel_name="TestChannel")
        mock_auth = MagicMock(spec=TwitchAuthManager)
        mock_auth.get_user_access_token.return_value = None
        mock_auth.has_tokens.return_value = False

        adapter = TwitchHelixAdapter(
            config=config,
            auth_manager=mock_auth,
        )

        result = adapter.update_stream_title("Sample Video")
        self.assertTrue(result)
        mock_auth.get_user_access_token.assert_called_once()


if __name__ == "__main__":
    unittest.main()
