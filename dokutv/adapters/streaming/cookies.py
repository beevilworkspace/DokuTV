"""
Cookie provider helper.
Configures cookie files or browser cookies for Streamlink and yt-dlp.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CookieProvider:
    """Manages cookie file/browser options for stream extractors."""

    def __init__(self, cookies_file: Optional[str] = None, cookies_browser: Optional[str] = None):
        self.cookies_file = cookies_file
        self.cookies_browser = cookies_browser

    def configure_streamlink(self, session: Any) -> None:
        """Load cookies into Streamlink session if available."""
        if self.cookies_file and os.path.exists(self.cookies_file):
            try:
                session.load_cookies(self.cookies_file)
            except Exception as e:
                logger.debug(f"Could not load cookies file for Streamlink: {e}")
        elif self.cookies_browser:
            try:
                session.set_option("cookies-from-browser", self.cookies_browser)
            except Exception as e:
                logger.debug(f"Could not set cookies-from-browser for Streamlink: {e}")

    def configure_ytdlp_opts(self, ydl_opts: Dict[str, Any]) -> None:
        """Apply cookie settings to yt-dlp options dictionary."""
        if self.cookies_file and os.path.exists(self.cookies_file):
            ydl_opts["cookiefile"] = os.path.abspath(self.cookies_file)
        elif self.cookies_browser:
            ydl_opts["cookiesfrombrowser"] = (self.cookies_browser,)
