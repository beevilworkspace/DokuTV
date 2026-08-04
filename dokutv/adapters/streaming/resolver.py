import logging
from typing import Optional, List
from dokutv.adapters.streaming.cookies import CookieProvider
from dokutv.adapters.streaming.models import ResolvedStream

logger = logging.getLogger(__name__)


class YoutubeUrlResolver:
    """Resolves video URLs to playable direct stream URLs (supporting 1080p+ dual video/audio DASH streams)."""

    def __init__(
        self,
        cookie_provider: Optional[CookieProvider] = None,
        quality_preference: Optional[List[str]] = None,
    ):
        self.cookie_provider = cookie_provider or CookieProvider()
        self.quality_preference = quality_preference or [
            "best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"
        ]

    def resolve_stream(self, youtube_url: str) -> Optional[ResolvedStream]:
        """Resolve a video URL into a ResolvedStream object (with optional separate audio URL for 1080p)."""
        if not youtube_url or not youtube_url.startswith("http"):
            return ResolvedStream(video_url=youtube_url, resolution="local")

        stream = self._resolve_ytdlp_dash(youtube_url)
        if stream:
            return stream

        streamlink_url = self._resolve_streamlink(youtube_url)
        if streamlink_url:
            return ResolvedStream(video_url=streamlink_url, resolution="streamlink")

        logger.error(f"FAILED: Could not resolve direct stream URL for '{youtube_url}'.")
        return None

    def resolve(self, youtube_url: str) -> Optional[str]:
        """Backward-compatible method returning video stream URL as string."""
        resolved = self.resolve_stream(youtube_url)
        return resolved.video_url if resolved else None

    def _resolve_ytdlp_dash(self, youtube_url: str) -> Optional[ResolvedStream]:
        """Stage 1: Resolve high-quality 1080p DASH streams (video + audio) using yt-dlp."""
        try:
            import yt_dlp
            logger.info(f"yt-dlp: Resolving high-quality stream for '{youtube_url}'...")
            ydl_opts = {
                "format": "bestvideo[height<=1080]+bestaudio/bestvideo+bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }
            self.cookie_provider.configure_ytdlp_opts(ydl_opts)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                if not info:
                    return None

                requested_formats = info.get("requested_formats")
                if requested_formats and len(requested_formats) >= 2:
                    video_fmt = requested_formats[0]
                    audio_fmt = requested_formats[1]
                    video_url = video_fmt.get("url")
                    audio_url = audio_fmt.get("url")
                    height = video_fmt.get("height") or info.get("height") or 1080

                    if video_url and audio_url:
                        logger.info(f"yt-dlp: Dual-stream (video {height}p + audio) resolved successfully.")
                        return ResolvedStream(
                            video_url=video_url,
                            audio_url=audio_url,
                            resolution=f"{height}p",
                            is_dual_input=True,
                        )

                single_url = info.get("url")
                if single_url:
                    height = info.get("height", "unknown")
                    logger.info(f"yt-dlp: Single progressive stream resolved ({height}p).")
                    return ResolvedStream(
                        video_url=single_url,
                        audio_url=None,
                        resolution=f"{height}p",
                        is_dual_input=False,
                    )
        except ImportError:
            logger.debug("yt-dlp is not installed.")
        except Exception as e:
            logger.warning(f"yt-dlp high quality resolution warning: {e}")

        return None

    def _resolve_streamlink(self, youtube_url: str) -> Optional[str]:
        """Stage 2: Fall back to Streamlink resolution."""
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
