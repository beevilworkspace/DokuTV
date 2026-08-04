"""
Twitch User OAuth Authorization Manager.
Orchestrates token storage, refresh, authorization flow, and server callbacks.
"""

import logging
import urllib.parse
from typing import Optional, Dict, Any

from dokutv.adapters.twitch_auth.twitch_tokens import TwitchTokens
from dokutv.adapters.twitch_auth.twitch_auth_config import TwitchAuthConfig
from dokutv.adapters.twitch_auth.twitch_token_store import TwitchTokenStore
from dokutv.adapters.twitch_auth.twitch_oauth_client import TwitchOAuthClient
from dokutv.adapters.twitch_auth.oauth_callback_server import OAuthCallbackServer
from dokutv.adapters.twitch_auth.browser_launcher import BrowserLauncher

logger = logging.getLogger(__name__)


class TwitchAuthManager:
    """Manages Twitch User OAuth tokens with automatic refresh."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        config: Optional[TwitchAuthConfig] = None,
        token_store: Optional[TwitchTokenStore] = None,
        oauth_client: Optional[TwitchOAuthClient] = None,
        callback_server: Optional[OAuthCallbackServer] = None,
        browser_launcher: Optional[BrowserLauncher] = None,
    ):
        self.config = config or TwitchAuthConfig.from_env(client_id=client_id, client_secret=client_secret)
        self.token_store = token_store or TwitchTokenStore(self.config.token_file)
        self.oauth_client = oauth_client or TwitchOAuthClient(self.config)
        self.callback_server = callback_server or OAuthCallbackServer()
        self.browser_launcher = browser_launcher or BrowserLauncher()

        self._cached_tokens: Optional[TwitchTokens] = self.token_store.load()

    @property
    def client_id(self) -> str:
        return self.config.client_id

    @client_id.setter
    def client_id(self, val: str) -> None:
        self.config.client_id = val

    @property
    def client_secret(self) -> str:
        return self.config.client_secret

    @client_secret.setter
    def client_secret(self, val: str) -> None:
        self.config.client_secret = val

    @property
    def _tokens(self) -> Optional[Dict[str, Any]]:
        """Backward-compatibility property returning tokens dictionary."""
        if self._cached_tokens:
            return self._cached_tokens.to_dict()
        return None

    @_tokens.setter
    def _tokens(self, val: Optional[Dict[str, Any]]) -> None:
        """Backward-compatibility setter for clearing or updating tokens."""
        if val is None:
            self._cached_tokens = None
            self.token_store.clear()
        else:
            self._cached_tokens = TwitchTokens.from_dict(val)
            self.token_store.save(self._cached_tokens)

    def has_tokens(self) -> bool:
        """Check if tokens have been obtained (initial auth completed)."""
        return self._cached_tokens is not None and bool(self._cached_tokens.refresh_token)

    def get_user_access_token(self) -> Optional[str]:
        """Get a valid User Access Token, refreshing automatically if expired."""
        if not self._cached_tokens:
            self._cached_tokens = self.token_store.load()

        if not self._cached_tokens:
            return None

        if not self._cached_tokens.is_expired(buffer_seconds=60.0):
            return self._cached_tokens.access_token

        logger.info("Twitch User Access Token expired. Refreshing automatically...")
        return self._refresh_token()

    def _refresh_token(self) -> Optional[str]:
        """Use the Refresh Token to obtain a new Access Token."""
        if not self._cached_tokens or not self._cached_tokens.refresh_token:
            logger.warning("No refresh token available. Re-run initial authorization.")
            return None

        new_tokens = self.oauth_client.refresh_token(self._cached_tokens.refresh_token)
        if new_tokens:
            self._cached_tokens = new_tokens
            self.token_store.save(new_tokens)
            logger.info("Twitch User Access Token refreshed successfully.")
            return new_tokens.access_token
        else:
            logger.error("Token refresh failed. Clearing invalid tokens.")
            self._tokens = None
            return None

    def run_initial_auth(self) -> bool:
        """Run the one-time OAuth2 Authorization Code flow."""
        if not self.config.client_id or not self.config.client_secret:
            logger.error("TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET must be set!")
            return False

        auth_url = self._build_authorization_url()

        logger.info(f"Opening browser for Twitch authorization. Redirect URI: {self.config.redirect_uri}")
        self.browser_launcher.open(auth_url)

        code = self._wait_for_callback()
        if not code:
            logger.error("Authorization failed (timeout or denied).")
            return False

        return self._exchange_code(code)

    def _build_authorization_url(self) -> str:
        """Build OAuth authorization redirect URL."""
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scopes,
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.config.endpoints.authorize_url}?{query_string}"

    def _wait_for_callback(self) -> Optional[str]:
        """Wait for local server to capture callback code."""
        logger.info("Waiting for Twitch authorization callback on port 3000 (max. 2 minutes)...")
        return self.callback_server.wait_for_code(timeout=120.0)

    def _exchange_code(self, code: str) -> bool:
        """Exchange authorization code for access and refresh tokens."""
        tokens = self.oauth_client.exchange_code(code)
        if tokens:
            self._cached_tokens = tokens
            self.token_store.save(tokens)
            logger.info("✅ Twitch User OAuth Token successfully obtained and stored!")
            return True
        else:
            logger.error("Token exchange failed.")
            return False
