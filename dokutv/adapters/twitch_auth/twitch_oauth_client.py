"""
OAuth HTTP Client component for Twitch API.
Encapsulates HTTP requests for OAuth token exchange and refresh.
"""

import json
import logging
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional
from dokutv.adapters.twitch_auth.twitch_auth_config import TwitchAuthConfig
from dokutv.adapters.twitch_auth.twitch_tokens import TwitchTokens

logger = logging.getLogger(__name__)


class TwitchOAuthClient:
    """Handles HTTP communication with Twitch OAuth2 token endpoint."""

    def __init__(self, config: TwitchAuthConfig):
        self.config = config

    def exchange_code(self, code: str) -> Optional[TwitchTokens]:
        """Exchange authorization code for Access and Refresh tokens."""
        data = urllib.parse.urlencode({
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.config.endpoints.token_url, data=data, method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            expires_in = result.get("expires_in", 14400)
            return TwitchTokens(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                expires_at=time.time() + expires_in,
            )

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Token exchange failed (HTTP {e.code}): {body}")
            return None
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, OSError) as e:
            logger.error(f"Token exchange error: {e}")
            return None

    def refresh_token(self, refresh_token: str) -> Optional[TwitchTokens]:
        """Obtain a new Access Token using a Refresh Token."""
        data = urllib.parse.urlencode({
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.config.endpoints.token_url, data=data, method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            expires_in = result.get("expires_in", 14400)
            new_refresh = result.get("refresh_token", refresh_token)
            return TwitchTokens(
                access_token=result["access_token"],
                refresh_token=new_refresh,
                expires_at=time.time() + expires_in,
            )

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Token refresh failed (HTTP {e.code}): {body}")
            return None
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, OSError) as e:
            logger.error(f"Token refresh error: {e}")
            return None
