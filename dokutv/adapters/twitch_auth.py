"""
Twitch OAuth2 Authorization Code Flow.

Handles User Access Token acquisition, storage, and automatic refresh.
Required for channel modifications (title, category) via Twitch Helix API.

Usage (one-time setup):
    python -m dokutv.adapters.twitch_auth

After initial authorization, tokens are stored in 'data/twitch_tokens.json'
and automatically refreshed – no manual action needed.
"""

import os
import json
import time
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict
from threading import Thread

from dokutv.infrastructure.env_config import load_env

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TwitchAuth")

TOKEN_FILE = "data/twitch_tokens.json"
REDIRECT_URI = "http://localhost:3000/callback"
SCOPES = "channel:manage:broadcast"


class _AuthCallbackHandler(BaseHTTPRequestHandler):
    """Temporary HTTP handler to capture the OAuth redirect callback."""
    auth_code: Optional[str] = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _AuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                "<h1>✅ Autorisierung erfolgreich!</h1>"
                "<p>Du kannst dieses Fenster schließen.</p>"
                "</body></html>".encode("utf-8")
            )
        else:
            error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                f"<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                f"<h1>❌ Fehler: {error}</h1>"
                f"</body></html>".encode("utf-8")
            )

    def log_message(self, format, *args):
        """Suppress default HTTP server request logging."""
        pass


class TwitchAuthManager:
    """Manages Twitch User OAuth tokens with automatic refresh."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        load_env()
        self.client_id = client_id or os.getenv("TWITCH_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("TWITCH_CLIENT_SECRET", "")
        self._tokens: Optional[Dict] = None
        self._load_tokens()

    # ── Token Persistence ──────────────────────────────────────────

    def _load_tokens(self) -> None:
        """Load saved tokens from disk."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    self._tokens = json.load(f)
                logger.info("Loaded saved Twitch User OAuth tokens.")
            except Exception:
                self._tokens = None

    def _save_tokens(self, access_token: str, refresh_token: str, expires_in: int) -> None:
        """Persist tokens to disk for automatic reuse."""
        self._tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": time.time() + expires_in,
        }
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(self._tokens, f, indent=2)
        logger.info("Twitch User OAuth tokens saved to disk.")

    # ── Token Access ───────────────────────────────────────────────

    def get_user_access_token(self) -> Optional[str]:
        """Get a valid User Access Token, refreshing automatically if expired."""
        if not self._tokens:
            return None

        # Token still valid (with 60s safety buffer)
        if time.time() < (self._tokens.get("expires_at", 0) - 60):
            return self._tokens["access_token"]

        # Token expired → refresh
        logger.info("Twitch User Access Token expired. Refreshing automatically...")
        return self._refresh_token()

    def has_tokens(self) -> bool:
        """Check if tokens have been obtained (initial auth completed)."""
        return self._tokens is not None and "refresh_token" in self._tokens

    # ── Token Refresh ──────────────────────────────────────────────

    def _refresh_token(self) -> Optional[str]:
        """Use the Refresh Token to obtain a new Access Token."""
        if not self._tokens or not self._tokens.get("refresh_token"):
            logger.warning("No refresh token available. Re-run initial authorization.")
            return None

        data = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self._tokens["refresh_token"],
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                "https://id.twitch.tv/oauth2/token", data=data, method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            self._save_tokens(
                access_token=result["access_token"],
                refresh_token=result.get("refresh_token", self._tokens["refresh_token"]),
                expires_in=result.get("expires_in", 14400),
            )
            logger.info("Twitch User Access Token refreshed successfully.")
            return result["access_token"]

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Token refresh failed (HTTP {e.code}): {body}")
            # Refresh token might be revoked – clear tokens
            self._tokens = None
            return None
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    # ── Initial Authorization Flow ─────────────────────────────────

    def run_initial_auth(self) -> bool:
        """Run the one-time OAuth2 Authorization Code flow.
        
        Opens a browser window for the user to log in and authorize the app.
        A temporary local HTTP server captures the callback.
        """
        if not self.client_id or not self.client_secret:
            print("FEHLER: TWITCH_CLIENT_ID und TWITCH_CLIENT_SECRET müssen in .env gesetzt sein!")
            return False

        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize?"
            f"response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
            f"&scope={urllib.parse.quote(SCOPES, safe='')}"
        )

        print("=" * 65)
        print("  DokuTV – Twitch OAuth2 Autorisierung (einmalig)")
        print("=" * 65)
        print()
        print("  WICHTIG: Stelle sicher, dass in deiner Twitch Developer Console")
        print(f"  die OAuth Redirect URL eingetragen ist:")
        print(f"    → {REDIRECT_URI}")
        print()
        print("  (https://dev.twitch.tv/console/apps → Deine App → Bearbeiten)")
        print()
        print("  Ein Browserfenster wird geöffnet...")
        print()

        # Reset any previous auth code
        _AuthCallbackHandler.auth_code = None

        # Start temporary local HTTP server
        try:
            server = HTTPServer(("localhost", 3000), _AuthCallbackHandler)
        except OSError as e:
            print(f"FEHLER: Konnte lokalen Server auf Port 3000 nicht starten: {e}")
            print("Ist Port 3000 bereits belegt?")
            return False

        server_thread = Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        # Open browser for user authorization
        webbrowser.open(auth_url)
        print("  Warte auf Twitch-Autorisierung im Browser... (max. 2 Minuten)")

        # Wait for the callback
        server_thread.join(timeout=120)
        server.server_close()

        auth_code = _AuthCallbackHandler.auth_code
        if not auth_code:
            print("\nFEHLER: Keine Autorisierung erhalten (Timeout oder abgelehnt).")
            return False

        # Exchange authorization code for tokens
        return self._exchange_code(auth_code)

    def _exchange_code(self, code: str) -> bool:
        """Exchange the authorization code for Access + Refresh tokens."""
        data = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                "https://id.twitch.tv/oauth2/token", data=data, method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            self._save_tokens(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                expires_in=result.get("expires_in", 14400),
            )

            print()
            print("  ✅ Twitch User OAuth Token erfolgreich erhalten und gespeichert!")
            print("     Der Token wird automatisch erneuert.")
            print("     Du musst diesen Schritt nicht mehr wiederholen.")
            print()
            return True

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"\nFEHLER: Token-Austausch fehlgeschlagen (HTTP {e.code}): {body}")
            return False
        except Exception as e:
            print(f"\nFEHLER: Token-Austausch fehlgeschlagen: {e}")
            return False


# ── CLI Entry Point ────────────────────────────────────────────────
# Run with: python -m dokutv.adapters.twitch_auth

if __name__ == "__main__":
    auth = TwitchAuthManager()
    success = auth.run_initial_auth()
    if not success:
        print("\nAutorisierung fehlgeschlagen. Bitte erneut versuchen.")
