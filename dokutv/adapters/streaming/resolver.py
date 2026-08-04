"""
YouTube URL resolver component.
Resolves YouTube/web URLs to direct streamable URLs using Streamlink and yt-dlp.
"""

import logging
from typing import Optional, List
from dokutv.adapters.streaming.cookies import CookieProvider

logger = logging.getLogger(__name__)


class YoutubeUrlResolver:
    """Resolves video URLs to playable direct stream URLs."""

    def __init__(
        self,
        cookie_provider: Optional[CookieProvider] = None,
        quality_preference: Optional[List[str]] = None,
    ):
        self.cookie_provider = cookie_provider or CookieProvider()
        self.quality_preference = quality_preference or [
            "best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"
        ]

    def resolve(self, youtube_url: str) -> Optional[str]:
        """Resolve a video URL to a direct stream URL."""
        if not youtube_url.startswith("http"):
            return youtube_url

        url = self._resolve_streamlink(youtube_url)
        if url:
            return url

        return self._resolve_ytdlp(youtube_url)

    def _resolve_streamlink(self, youtube_url: str) -> Optional[str]:
        """Stage 1: Try Streamlink resolution."""
        try:
            import streamlink
            logger.info(f"Streamlink: Resolving direct stream URL for: '{youtube_url}'...")
            session = streamlink.Streamlink()
            self.cookie_provider.configure_streamlink(session)

            streams = session.streams(youtube_url)
            if streams:
                for quality in self.quality_preference:
                    if quality in streams:
                        direct_url = streams[quality].url
                        logger.info(f"Streamlink: Selected '{quality}' stream.")
                        return direct_url
        except ImportError:
            logger.debug("Streamlink is not installed.")
        except Exception as e:
            logger.warning(f"Streamlink resolution warning: {e}")

        return None

    def _resolve_ytdlp(self, youtube_url: str) -> Optional[str]:
        """Stage 2: Fall back to yt-dlp resolution."""
        try:
            import yt_dlp
            logger.info(f"Falling back to yt-dlp for URL resolution of '{youtube_url}'...")
            ydl_opts = {
                "format": "best[height<=1080]/best",
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }
            self.cookie_provider.configure_ytdlp_opts(ydl_opts)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                direct_url = info.get("url")
                if direct_url:
                    logger.info("yt-dlp: Direct stream URL resolved successfully.")
                    return direct_url
        except ImportError:
            logger.debug("yt-dlp is not installed.")
        except Exception as e:
            logger.warning(f"yt-dlp fallback failed: {e}")

        logger.error(f"FAILED: Could not resolve direct stream URL for '{youtube_url}'.")
        return None
