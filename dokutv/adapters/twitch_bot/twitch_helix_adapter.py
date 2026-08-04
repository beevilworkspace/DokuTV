"""
Interface Adapters - Twitch Helix API Bot.
Implements TwitchPort.
Orchestrates Twitch Helix API updates using User Access Tokens.
"""

import logging
import urllib.error
from typing import Optional

from dokutv.application.ports import TwitchPort
from dokutv.adapters.twitch_auth import TwitchAuthManager
from dokutv.adapters.twitch_bot.twitch_helix_config import TwitchHelixConfig
from dokutv.adapters.twitch_bot.twitch_title_formatter import TwitchTitleFormatter
from dokutv.adapters.twitch_bot.twitch_helix_client import TwitchHelixClient

logger = logging.getLogger(__name__)


class TwitchHelixAdapter(TwitchPort):
    """Adapter for updating Twitch channel status via Twitch Helix API."""

    def __init__(
        self,
        channel_name: str = "DokuTV_EN",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        config: Optional[TwitchHelixConfig] = None,
        auth_manager: Optional[TwitchAuthManager] = None,
        client: Optional[TwitchHelixClient] = None,
        title_formatter: Optional[TwitchTitleFormatter] = None,
    ):
        self.config = config or TwitchHelixConfig.from_env(
            channel_name=channel_name,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.auth_manager = auth_manager or TwitchAuthManager(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
        )
        self.client = client or TwitchHelixClient(self.config)
        self.title_formatter = title_formatter or TwitchTitleFormatter(self.config)

    @property
    def channel_name(self) -> str:
        return self.config.channel_name

    @channel_name.setter
    def channel_name(self, val: str) -> None:
        self.config.channel_name = val

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
    def _broadcaster_id(self) -> Optional[str]:
        return self.client._broadcaster_id_cache

    @_broadcaster_id.setter
    def _broadcaster_id(self, val: Optional[str]) -> None:
        self.client._broadcaster_id_cache = val

    @property
    def _app_token(self) -> Optional[str]:
        return self.client._app_token

    def update_stream_title(self, video_title: str) -> bool:
        """Update the Twitch channel title and category using a User Access Token."""
        formatted_title = self.title_formatter.format_title(video_title)
        logger.info(f"Updating Twitch channel '{self.channel_name}' title to: '{formatted_title}'")
        logger.info(f"Setting Twitch category to ID={self.config.default_category_id}.")

        user_token = self.auth_manager.get_user_access_token()
        if not user_token:
            if not self.auth_manager.has_tokens():
                logger.warning(
                    "Kein User OAuth Token vorhanden! "
                    "Führe einmalig aus: python -m dokutv.adapters.twitch_auth"
                )
            logger.info(f"[Dry Run] Simulated title: '{formatted_title}', category ID: {self.config.default_category_id}")
            return True

        broadcaster_id = self.client.get_broadcaster_id(self.channel_name, user_token)
        if not broadcaster_id:
            return False

        try:
            return self.client.update_channel_info(
                broadcaster_id=broadcaster_id,
                user_token=user_token,
                title=formatted_title,
                category_id=self.config.default_category_id,
            )
        except urllib.error.HTTPError as http_err:
            if http_err.code == 401:
                self.auth_manager._tokens = None
            return False
