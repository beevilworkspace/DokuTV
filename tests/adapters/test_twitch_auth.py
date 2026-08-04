import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from dokutv.adapters.twitch_auth import (
    TwitchTokens,
    TwitchAuthConfig,
    TwitchTokenStore,
    TwitchOAuthClient,
    BrowserLauncher,
    TwitchAuthManager,
)


class TestTwitchAuthAdapter(unittest.TestCase):

    def test_twitch_tokens_expiry(self):
        now = time.time()
        tokens = TwitchTokens(
            access_token="acc123",
            refresh_token="ref123",
            expires_at=now + 100
        )
        self.assertFalse(tokens.is_expired(buffer_seconds=60))

        expired_tokens = TwitchTokens(
            access_token="acc123",
            refresh_token="ref123",
            expires_at=now + 30
        )
        self.assertTrue(expired_tokens.is_expired(buffer_seconds=60))

    def test_twitch_token_store_persistence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            token_path = Path(tmpdir) / "tokens.json"
            store = TwitchTokenStore(token_path)

            self.assertFalse(store.exists())
            self.assertIsNone(store.load())

            tokens = TwitchTokens(access_token="a1", refresh_token="r1", expires_at=12345.0)
            store.save(tokens)

            self.assertTrue(store.exists())
            loaded = store.load()
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.access_token, "a1")
            self.assertEqual(loaded.refresh_token, "r1")

            store.clear()
            self.assertFalse(store.exists())
            self.assertIsNone(store.load())

    def test_twitch_auth_config_defaults(self):
        config = TwitchAuthConfig(client_id="test_id", client_secret="test_secret")
        self.assertEqual(config.client_id, "test_id")
        self.assertIn("localhost", config.redirect_uri)

    def test_twitch_auth_manager_di(self):
        config = TwitchAuthConfig(client_id="id123", client_secret="sec123")
        mock_client = MagicMock(spec=TwitchOAuthClient)
        mock_store = MagicMock(spec=TwitchTokenStore)
        mock_browser = MagicMock(spec=BrowserLauncher)

        mock_store.load.return_value = TwitchTokens(
            access_token="valid_acc",
            refresh_token="valid_ref",
            expires_at=time.time() + 3600
        )

        manager = TwitchAuthManager(
            config=config,
            token_store=mock_store,
            oauth_client=mock_client,
            browser_launcher=mock_browser,
        )

        self.assertTrue(manager.has_tokens())
        self.assertEqual(manager.get_user_access_token(), "valid_acc")


if __name__ == "__main__":
    unittest.main()
