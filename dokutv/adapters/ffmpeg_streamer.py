"""
Interface Adapters - FFmpeg Live Streamer.
Implements StreamerPort.
Uses MPEG-TS piping into a persistent FFmpeg RTMP process for true 24/7 continuous Twitch streaming.
"""

import os
import shutil
import subprocess
import logging
import time
from typing import Optional

from dokutv.application.ports import StreamerPort

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FFmpegStreamerAdapter")

TWITCH_RTMP_URL = "rtmp://live.twitch.tv/app"


class FFmpegStreamerAdapter(StreamerPort):
    def __init__(self, stream_key: Optional[str] = None):
        self.stream_key = stream_key or os.getenv("TWITCH_STREAM_KEY", "")
        self.persistent_process: Optional[subprocess.Popen] = None

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

    def start_persistent_stream(self) -> bool:
        """Start a single continuous RTMP process to Twitch reading MPEG-TS from stdin."""
        if not self.stream_key or self.stream_key.startswith("live_123456789"):
            logger.info("[Dry Run / Simulation] Persistent stream started (Simulated).")
            return True

        ffmpeg_bin = self.get_ffmpeg_binary_path()
        if not ffmpeg_bin:
            logger.error("[FEHLER] 'ffmpeg' wurde auf Ihrem System nicht gefunden!")
            return False

        target_rtmp = f"{TWITCH_RTMP_URL}/{self.stream_key}"
        cmd = [
            ffmpeg_bin,
            "-re",
            "-f", "mpegts",
            "-i", "pipe:0",
            "-c:v", "copy",
            "-c:a", "copy",
            "-f", "flv",
            target_rtmp
        ]

        try:
            logger.info("Initializing persistent MPEG-TS → RTMP stream to Twitch...")
            self.persistent_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info("✅ Persistent RTMP stream connected to Twitch! (Channel stays LIVE)")
            return True
        except Exception as e:
            logger.error(f"Failed to start persistent RTMP stream: {e}")
            self.persistent_process = None
            return False

    def stop_persistent_stream(self) -> None:
        """Close stdin and terminate persistent RTMP stream process."""
        if self.persistent_process:
            logger.info("Closing persistent RTMP stream to Twitch...")
            try:
                if self.persistent_process.stdin:
                    self.persistent_process.stdin.close()
                self.persistent_process.terminate()
                self.persistent_process.wait(timeout=3)
            except Exception as e:
                logger.warning(f"Error terminating persistent stream: {e}")
            finally:
                self.persistent_process = None
            logger.info("Persistent RTMP stream closed.")

    def resolve_stream_url(self, youtube_url: str) -> Optional[str]:
        """Resolve a YouTube URL to a direct stream URL using Streamlink / yt-dlp."""
        if not youtube_url.startswith("http"):
            return youtube_url

        cookies_file = os.getenv("YOUTUBE_COOKIES_FILE") or ("cookies.txt" if os.path.exists("cookies.txt") else None)
        cookies_browser = os.getenv("YOUTUBE_COOKIES_BROWSER")

        # Stage 1: Streamlink
        try:
            import streamlink
            logger.info(f"Streamlink: Resolving direct stream URL for: '{youtube_url}'...")
            session = streamlink.Streamlink()

            if cookies_file and os.path.exists(cookies_file):
                try:
                    session.load_cookies(cookies_file)
                except Exception:
                    pass
            elif cookies_browser:
                try:
                    session.set_option("cookies-from-browser", cookies_browser)
                except Exception:
                    pass

            streams = session.streams(youtube_url)
            if streams:
                for quality in ["best", "1080p60", "1080p", "720p60", "720p", "480p", "360p", "worst"]:
                    if quality in streams:
                        direct_url = streams[quality].url
                        logger.info(f"Streamlink: Selected '{quality}' stream.")
                        return direct_url
        except Exception as e:
            logger.warning(f"Streamlink resolution warning: {e}")

        # Stage 2: yt-dlp fallback
        try:
            import yt_dlp
            logger.info(f"Falling back to yt-dlp for URL resolution of '{youtube_url}'...")
            ydl_opts = {
                'format': 'best[height<=1080]/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            if cookies_file and os.path.exists(cookies_file):
                ydl_opts['cookiefile'] = os.path.abspath(cookies_file)
            elif cookies_browser:
                ydl_opts['cookiesfrombrowser'] = (cookies_browser,)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                direct_url = info.get('url')
                if direct_url:
                    logger.info("yt-dlp: Direct stream URL resolved successfully.")
                    return direct_url
        except Exception as e:
            logger.warning(f"yt-dlp fallback failed: {e}")

        logger.error(f"FAILED: Could not resolve direct stream URL for '{youtube_url}'.")
        return None

    def build_feeder_command(self, ffmpeg_bin: str, input_source: str, duration_limit: Optional[int] = None) -> list:
        """Build FFmpeg command to decode input_source into MPEG-TS byte stream."""
        cmd = [ffmpeg_bin, "-re"]
        if duration_limit:
            cmd.extend(["-t", str(duration_limit)])
        cmd.extend([
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
            "-f", "mpegts",
            "pipe:1"
        ])
        return cmd

    def stream_video(self, input_source: str, video_title: str, duration_limit: Optional[int] = None, block: bool = True) -> bool:
        """Stream a video seamlessly into the persistent MPEG-TS stream."""
        ffmpeg_bin = self.get_ffmpeg_binary_path()
        if not ffmpeg_bin:
            logger.error("[FEHLER] 'ffmpeg' wurde auf Ihrem System nicht gefunden!")
            return False

        direct_url = self.resolve_stream_url(input_source)
        if not direct_url:
            logger.error(f"Skipping '{video_title}' – no playable stream URL available.")
            return False

        logger.info(f"Preparing stream for: '{video_title}'")

        # Simulation Mode / Dry Run
        if not self.stream_key or self.stream_key.startswith("live_123456789"):
            sim_time = min(duration_limit or 10, 10)
            logger.info(f"[Dry Run / Simulation] Streaming '{video_title}' for {sim_time} seconds...")
            time.sleep(sim_time)
            logger.info(f"[Dry Run / Simulation] Finished streaming '{video_title}'.")
            return True

        # Case A: Persistent MPEG-TS Stream is active
        if self.persistent_process and self.persistent_process.poll() is None and self.persistent_process.stdin:
            logger.info(f"Feeding '{video_title}' into persistent MPEG-TS stream (Twitch stays LIVE)...")
            cmd = self.build_feeder_command(ffmpeg_bin, direct_url, duration_limit=duration_limit)
            try:
                feeder_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL
                )

                buf_size = 64 * 1024
                while True:
                    data = feeder_proc.stdout.read(buf_size)
                    if not data:
                        break
                    try:
                        self.persistent_process.stdin.write(data)
                        self.persistent_process.stdin.flush()
                    except (BrokenPipeError, OSError) as write_err:
                        logger.error(f"Persistent stream stdin write error: {write_err}")
                        break

                feeder_proc.wait()
                logger.info(f"Finished feeding '{video_title}' to MPEG-TS stream. Pipe remains OPEN for next video!")
                return True
            except Exception as e:
                logger.error(f"Error feeding stream: {e}")
                return False

        # Case B: Fallback Standalone stream
        logger.warning("Persistent stream stdin unavailable. Launching standalone RTMP stream...")
        target_rtmp = f"{TWITCH_RTMP_URL}/{self.stream_key}"
        cmd = [ffmpeg_bin, "-re"]
        if duration_limit:
            cmd.extend(["-t", str(duration_limit)])
        cmd.extend([
            "-i", direct_url,
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
        ])
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if block:
                proc.wait()
            return True
        except Exception as e:
            logger.error(f"Standalone streaming error: {e}")
            return False
