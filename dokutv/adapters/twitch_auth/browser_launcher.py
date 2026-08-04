"""
Browser launcher component for OAuth flow.
Encapsulates opening authorization URLs in external browser.
"""

import logging
import webbrowser

logger = logging.getLogger(__name__)


class BrowserLauncher:
    """Launches system default web browser."""

    def open(self, url: str) -> bool:
        """Open given URL in default browser."""
        logger.info(f"Opening browser for URL: {url}")
        try:
            return webbrowser.open(url)
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            return False
