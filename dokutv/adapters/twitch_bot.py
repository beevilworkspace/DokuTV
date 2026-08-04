"""
Interface Adapters - Twitch Helix API Bot.
Implements TwitchPort.

Uses User Access Token (via TwitchAuthManager) for channel modifications.
Falls back to App Access Token for read-only operations.
"""

import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
from typing import Optional

from dokutv.application.ports import TwitchPort
from dokutv.infrastructure.env_config import load_env
from dokutv.adapters.twitch_auth import TwitchAuthManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TwitchHelixAdapter")

# "Just Chatting" category – the successor to the old "IRL" category on Twitch.
TWITCH_CATEGORY_ID = "509658"


class TwitchHelixAdapter(TwitchPort):
    def __init__(self, channel_name: str = "DokuTV_EN", client_id: Optional[str] = None, client_secret: Optional[str] = None):
        load_env()
        self.channel_name = channel_name
        self.client_id = client_id or os.getenv("TWITCH_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("TWITCH_CLIENT_SECRET", "")

        # User OAuth token manager (for channel modifications)
        self.auth_manager = TwitchAuthManager(self.client_id, self.client_secret)

        # Cached broadcaster ID (looked up once, reused)
        self._broadcaster_id: Optional[str] = None

        # App Access Token fallback (for read-only operations like user lookup)
        self._app_token: Optional[str] = None
        self._app_token_expiry: float = 0.0

    def _get_app_access_token(self) -> Optional[str]:
        """Get an App Access Token (client_credentials) for read-only API calls."""
        if self._app_token and time.time() < (self._app_token_expiry - 60):
            return self._app_token

        if not self.client_id or not self.client_secret:
            return None

        data = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                "https://id.twitch.tv/oauth2/token", data=data, method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            self._app_token = result.get("access_token")
            self._app_token_expiry = time.time() + result.get("expires_in", 3600)
            return self._app_token
        except Exception as e:
            logger.error(f"Failed to fetch App Access Token: {e}")
            return None

    def _get_broadcaster_id(self, token: str) -> Optional[str]:
        """Look up and cache the broadcaster ID for the channel."""
        if self._broadcaster_id:
            return self._broadcaster_id

        try:
            user_url = f"https://api.twitch.tv/helix/users?login={self.channel_name.lower()}"
            req = urllib.request.Request(user_url, headers={
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {token}"
            })
            with urllib.request.urlopen(req) as resp:
                user_data = json.loads(resp.read().decode("utf-8"))

            users = user_data.get("data", [])
            if not users:
                logger.error(f"Broadcaster '{self.channel_name}' not found on Twitch.")
                return None

            self._broadcaster_id = users[0]["id"]
            logger.info(f"Broadcaster ID for '{self.channel_name}': {self._broadcaster_id}")
            return self._broadcaster_id

        except Exception as e:
            logger.error(f"Failed to look up broadcaster ID: {e}")
            return None

    def update_stream_title(self, video_title: str) -> bool:
        """Update the Twitch channel title and category using a User Access Token."""
        formatted_title = f"🔴 24/7 Doku: {video_title} | DokuTV_EN"
        logger.info(f"Updating Twitch channel '{self.channel_name}' title to: '{formatted_title}'")
        logger.info(f"Setting Twitch category to 'Just Chatting' (game_id={TWITCH_CATEGORY_ID}).")

        # ── Get User Access Token (required for channel modifications) ──
        user_token = self.auth_manager.get_user_access_token()
        if not user_token:
            if not self.auth_manager.has_tokens():
                logger.warning(
                    "Kein User OAuth Token vorhanden! "
                    "Führe einmalig aus: python -m dokutv.adapters.twitch_auth"
                )
            logger.info(f"[Dry Run] Simulated title: '{formatted_title}', category: Just Chatting")
            return True

        # ── Look up broadcaster ID ──
        broadcaster_id = self._get_broadcaster_id(user_token)
        if not broadcaster_id:
            return False

        # ── PATCH channel info (title + category) ──
        try:
            patch_url = f"https://api.twitch.tv/helix/channels?broadcaster_id={broadcaster_id}"
            payload = json.dumps({
                "title": formatted_title,
                "game_id": TWITCH_CATEGORY_ID,
            }).encode("utf-8")

            patch_req = urllib.request.Request(patch_url, data=payload, method="PATCH", headers={
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(patch_req):
                logger.info(f"✅ Twitch: Title + Category updated successfully!")
                return True

        except urllib.error.HTTPError as http_err:
            if http_err.code == 401:
                logger.warning(
                    "Twitch API 401: User Access Token ungültig oder abgelaufen. "
                    "Führe erneut aus: python -m dokutv.adapters.twitch_auth"
                )
                # Clear cached tokens so they get refreshed on next attempt
                self.auth_manager._tokens = None
            else:
                body = http_err.read().decode("utf-8", errors="replace")
                logger.warning(f"Twitch API HTTP error {http_err.code}: {body}")
            return False
        except Exception as e:
            logger.error(f"Error updating Twitch channel: {e}")
            return False
