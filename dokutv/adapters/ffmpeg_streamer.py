"""
Interface Adapters - FFmpeg Live Streamer.
Implements StreamerPort.
Uses Streamlink for reliable YouTube URL resolution (no deno/external JS runtime needed).
"""

import os
import shutil
import subprocess
import logging
from typing import Optional

from dokutv.application.ports import StreamerPort

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FFmpegStreamerAdapter")

TWITCH_RTMP_URL = "rtmp://live.twitch.tv/app"


class FFmpegStreamerAdapter(StreamerPort):
    def __init__(self, stream_key: Optional[str] = None):
        self.stream_key = stream_key or os.getenv("TWITCH_STREAM_KEY", "")

    def get_ffmpeg_binary_path(self) -> Optional[str]:
        """Locate FFmpeg binary: local file → imageio_ffmpeg → system PATH."""
        if os.path.exists("ffmpeg.exe"):
            return os.path.abspath("ffmpeg.exe")

        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_exe and os.path.exists(ffmpeg_exe):
                return ffmpeg_exe
        except ImportError:
            pass

        which_path = shutil.which("ffmpeg")
        if which_path:
            return which_path

        return None

    def resolve_stream_url(self, youtube_url: str) -> Optional[str]:
        """Resolve a YouTube URL to a direct stream URL using Streamlink.
        
        Returns the direct URL on success, or None if resolution fails.
        Never returns a raw YouTube page URL – that would cause FFmpeg to fail silently.
        """
        if not youtube_url.startswith("http"):
            return youtube_url

        # --- Stage 1: Streamlink (primary, no external runtime dependencies) ---
        try:
            import streamlink
            logger.info(f"Streamlink: Resolving direct stream URL for: '{youtube_url}'...")
            streams = streamlink.streams(youtube_url)

            if not streams:
                logger.warning(f"Streamlink: No streams found for '{youtube_url}'.")
                return None

            available = list(streams.keys())
            logger.info(f"Streamlink: Available qualities: {available}")

            # Select highest quality available stream
            for quality in ["best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"]:
                if quality in streams:
                    direct_url = streams[quality].url
                    logger.info(f"Streamlink: Selected '{quality}' stream.")
                    return direct_url

        except ImportError:
            logger.error("Streamlink is not installed! Run: pip install streamlink")
        except Exception as e:
            logger.warning(f"Streamlink: Could not resolve '{youtube_url}': {e}")

        # --- Stage 2: yt-dlp fallback (if still installed) ---
        try:
            import yt_dlp
            logger.info("Falling back to yt-dlp for URL resolution...")
            ydl_opts = {'format': 'best[height<=1080]', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                direct_url = info.get('url')
                if direct_url:
                    logger.info("yt-dlp: Direct stream URL resolved successfully.")
                    return direct_url
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"yt-dlp fallback failed: {e}")

        # --- No resolution possible → return None (don't pass raw YouTube URL) ---
        logger.error(f"FAILED: Could not resolve direct stream URL for '{youtube_url}'. Skipping this video.")
        return None

    def build_ffmpeg_command(self, ffmpeg_bin: str, input_source: str, title: str) -> list:
        """Build the FFmpeg command for RTMP streaming to Twitch."""
        target_rtmp = f"{TWITCH_RTMP_URL}/{self.stream_key}"
        return [
            ffmpeg_bin,
            "-re",
            "-i", input_source,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-maxrate", "6000k",
            "-bufsize", "12000k",
            "-pix_fmt", "yuv420p",
            "-g", "120",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", "44100",
            "-f", "flv",
            target_rtmp
        ]

    def stream_video(self, input_source: str, video_title: str) -> bool:
        """Stream a video to Twitch via FFmpeg."""
        ffmpeg_bin = self.get_ffmpeg_binary_path()
        if not ffmpeg_bin:
            logger.error("[FEHLER] 'ffmpeg' wurde auf Ihrem System nicht gefunden!")
            return False

        direct_url = self.resolve_stream_url(input_source)
        if not direct_url:
            logger.error(f"Skipping '{video_title}' – no playable stream URL available.")
            return False

        logger.info(f"Preparing to stream: '{video_title}' with FFmpeg ({ffmpeg_bin})")
        cmd = self.build_ffmpeg_command(ffmpeg_bin, direct_url, video_title)
        
        if not self.stream_key or self.stream_key.startswith("live_123456789"):
            logger.info("[Dry Run] Stream key placeholder. Simulation successful.")
            return True
            
        try:
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logger.info(f"FFmpeg Streaming process launched successfully for '{video_title}'!")
            return True
        except FileNotFoundError:
            logger.error("FFmpeg executable not found.")
            return False
        except Exception as e:
            logger.error(f"FFmpeg streaming error: {e}")
            return False

