"""
Twitch OAuth2 Authorization Code Flow.

Re-exports TwitchAuthManager from the twitch_auth subpackage.
Provides CLI entry point for initial one-time setup:
    python -m dokutv.adapters.twitch_auth
"""

import sys
from dokutv.adapters.twitch_auth.twitch_tokens import TwitchTokens
from dokutv.adapters.twitch_auth.twitch_auth_config import TwitchAuthConfig
from dokutv.adapters.twitch_auth.twitch_token_store import TwitchTokenStore
from dokutv.adapters.twitch_auth.twitch_oauth_client import TwitchOAuthClient
from dokutv.adapters.twitch_auth.oauth_callback_server import OAuthCallbackServer
from dokutv.adapters.twitch_auth.browser_launcher import BrowserLauncher
from dokutv.adapters.twitch_auth.twitch_auth_manager import TwitchAuthManager

__all__ = [
    "TwitchAuthManager",
    "TwitchTokens",
    "TwitchAuthConfig",
    "TwitchTokenStore",
    "TwitchOAuthClient",
    "OAuthCallbackServer",
    "BrowserLauncher",
]


if __name__ == "__main__":
    auth = TwitchAuthManager()
    print("=" * 65)
    print("  DokuTV – Twitch OAuth2 Autorisierung (einmalig)")
    print("=" * 65)
    print(f"  Redirect URI: {auth.config.redirect_uri}")
    print()
    success = auth.run_initial_auth()
    if not success:
        print("\nAutorisierung fehlgeschlagen. Bitte erneut versuchen.")
        sys.exit(1)
    print("\n✅ Autorisierung erfolgreich abgeschlossen!")
