"""
OAuth callback server component.
Listens on local HTTP port to capture the OAuth authorization code callback.
"""

import logging
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from queue import Queue
from threading import Thread
from typing import Optional

logger = logging.getLogger(__name__)


def make_callback_handler(result_queue: Queue):
    """Factory function for creating HTTP handler bound to a thread-safe Queue."""

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if "code" in params:
                code = params["code"][0]
                result_queue.put(code)
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
                result_queue.put(None)
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    f"<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                    f"<h1>❌ Fehler: {error}</h1>"
                    f"</body></html>".encode("utf-8")
                )

        def log_message(self, format, *args):
            """Suppress HTTP server log noise."""
            pass

    return CallbackHandler


class OAuthCallbackServer:
    """Manages temporary HTTP server lifecycle to wait for OAuth callback code."""

    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port

    def wait_for_code(self, timeout: float = 120.0) -> Optional[str]:
        """Start local HTTP server, wait for OAuth callback code, and return code."""
        result_queue: Queue = Queue()
        handler_cls = make_callback_handler(result_queue)

        try:
            server = HTTPServer((self.host, self.port), handler_cls)
        except OSError as e:
            logger.error(f"Failed to start callback server on {self.host}:{self.port}: {e}")
            return None

        server_thread = Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        try:
            code = result_queue.get(timeout=timeout)
        except Exception:
            code = None
        finally:
            server.server_close()

        return code
