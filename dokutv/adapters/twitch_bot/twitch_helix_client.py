"""
Twitch Helix HTTP API client component.
Encapsulates HTTP requests for broadcaster lookup, app tokens, and channel info updates.
"""

import json
import time
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional

from dokutv.adapters.twitch_bot.twitch_helix_config import TwitchHelixConfig

logger = logging.getLogger(__name__)


class TwitchHelixClient:
    """Handles HTTP communication with Twitch Helix endpoints."""

    def __init__(self, config: TwitchHelixConfig):
        self.config = config
        self._app_token: Optional[str] = None
        self._app_token_expiry: float = 0.0
        self._broadcaster_id_cache: Optional[str] = None

    def get_app_access_token(self) -> Optional[str]:
        """Get an App Access Token (client_credentials) for read-only API calls."""
        if self._app_token and time.time() < (self._app_token_expiry - 60.0):
            return self._app_token

        if not self.config.client_id or not self.config.client_secret:
            return None

        data = urllib.parse.urlencode({
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "client_credentials",
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.config.endpoints.token_url, data=data, method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            self._app_token = result.get("access_token")
            self._app_token_expiry = time.time() + float(result.get("expires_in", 3600))
            return self._app_token

        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError, OSError) as e:
            logger.error(f"Failed to fetch App Access Token: {e}")
            return None

    def get_broadcaster_id(self, channel_name: str, token: str) -> Optional[str]:
        """Look up and cache the broadcaster ID for the channel."""
        if self._broadcaster_id_cache:
            return self._broadcaster_id_cache

        try:
            user_url = f"{self.config.endpoints.users_url}?login={channel_name.lower()}"
            req = urllib.request.Request(user_url, headers={
                "Client-ID": self.config.client_id,
                "Authorization": f"Bearer {token}",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                user_data = json.loads(resp.read().decode("utf-8"))

            users = user_data.get("data", [])
            if not users:
                logger.error(f"Broadcaster '{channel_name}' not found on Twitch.")
                return None

            self._broadcaster_id_cache = users[0]["id"]
            logger.info(f"Broadcaster ID for '{channel_name}': {self._broadcaster_id_cache}")
            return self._broadcaster_id_cache

        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError, OSError) as e:
            logger.error(f"Failed to look up broadcaster ID: {e}")
            return None

    def update_channel_info(
        self,
        broadcaster_id: str,
        user_token: str,
        title: str,
        category_id: str,
    ) -> bool:
        """PATCH channel info (title and category) on Twitch Helix API."""
        try:
            patch_url = f"{self.config.endpoints.channels_url}?broadcaster_id={broadcaster_id}"
            payload = json.dumps({
                "title": title,
                "game_id": category_id,
            }).encode("utf-8")

            patch_req = urllib.request.Request(patch_url, data=payload, method="PATCH", headers={
                "Client-ID": self.config.client_id,
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            })
            with urllib.request.urlopen(patch_req, timeout=15):
                logger.info("✅ Twitch: Title + Category updated successfully!")
                return True

        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode("utf-8", errors="replace")
            if http_err.code == 401:
                logger.warning(
                    "Twitch API 401: User Access Token invalid or expired. "
                    "Run initial auth: python -m dokutv.adapters.twitch_auth"
                )
            else:
                logger.warning(f"Twitch API HTTP error {http_err.code}: {body}")
            raise http_err
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            logger.error(f"Error updating Twitch channel info: {e}")
            return False
