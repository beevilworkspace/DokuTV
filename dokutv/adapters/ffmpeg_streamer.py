"""
Interface Adapters - FFmpeg Live Streamer.
Implements StreamerPort.
Orchestrates streaming components (Locator, Resolver, CommandBuilder, Session, Target).
"""

import os
import time
import subprocess
import logging
from typing import Optional, List

from dokutv.application.ports import StreamerPort
from dokutv.adapters.streaming import (
    StreamingConfig,
    StreamingTarget,
    TwitchTarget,
    FFmpegBinaryLocator,
    YoutubeUrlResolver,
    FFmpegCommandBuilder,
    PersistentStreamSession,
    StreamResult,
)

logger = logging.getLogger(__name__)


class FFmpegStreamerAdapter(StreamerPort):
    """Facade orchestrating FFmpeg streaming operations."""

    def __init__(
        self,
        stream_key: Optional[str] = None,
        target: Optional[StreamingTarget] = None,
        locator: Optional[FFmpegBinaryLocator] = None,
        resolver: Optional[YoutubeUrlResolver] = None,
        command_builder: Optional[FFmpegCommandBuilder] = None,
        config: Optional[StreamingConfig] = None,
    ):
        self.config = config or StreamingConfig.from_env()
        self.stream_key = stream_key or os.getenv("TWITCH_STREAM_KEY", "")
        self.target = target or TwitchTarget()
        self.locator = locator or FFmpegBinaryLocator()
        self.resolver = resolver or YoutubeUrlResolver(quality_preference=self.config.quality_preference)
        self.command_builder = command_builder or FFmpegCommandBuilder(config=self.config)
        self.session = PersistentStreamSession()

    @property
    def persistent_process(self) -> Optional[subprocess.Popen]:
        """Backward-compatibility property for accessing underlying process."""
        return self.session.process

    @persistent_process.setter
    def persistent_process(self, proc: Optional[subprocess.Popen]) -> None:
        self.session.process = proc

    @property
    def is_simulation(self) -> bool:
        """Central check for dry-run / simulation mode."""
        return not self.stream_key or self.stream_key.startswith("live_123456789")

    def get_ffmpeg_binary_path(self) -> Optional[str]:
        """Locate FFmpeg binary."""
        return self.locator.find()

    def start_persistent_stream(self) -> bool:
        """Start a single continuous RTMP process reading MPEG-TS from stdin."""
        if self.is_simulation:
            logger.info("[Dry Run / Simulation] Persistent stream started (Simulated).")
            return True

        ffmpeg_bin = self.get_ffmpeg_binary_path()
        if not ffmpeg_bin:
            return False

        target_rtmp = self.target.get_rtmp_url(self.stream_key)
        cmd = self.command_builder.build_persistent_rtmp_command(ffmpeg_bin, target_rtmp)
        return self.session.start(cmd)

    def stop_persistent_stream(self) -> None:
        """Close stdin and terminate persistent RTMP stream process."""
        self.session.stop()

    def resolve_stream_url(self, youtube_url: str) -> Optional[str]:
        """Resolve a YouTube URL to a direct stream URL."""
        return self.resolver.resolve(youtube_url)

    def build_feeder_command(
        self,
        ffmpeg_bin: str,
        input_source: str,
        duration_limit: Optional[int] = None,
    ) -> List[str]:
        """Build FFmpeg command to decode input_source into MPEG-TS byte stream."""
        return self.command_builder.build_feeder_command(ffmpeg_bin, input_source, duration_limit)

    def stream_video(
        self,
        input_source: str,
        video_title: str,
        duration_limit: Optional[int] = None,
        block: bool = True,
    ) -> bool:
        """Stream a video seamlessly into the persistent MPEG-TS stream."""
        result = self.stream_video_detailed(
            input_source=input_source,
            video_title=video_title,
            duration_limit=duration_limit,
            block=block,
        )
        return result.success

    def stream_video_detailed(
        self,
        input_source: str,
        video_title: str,
        duration_limit: Optional[int] = None,
        block: bool = True,
    ) -> StreamResult:
        """Stream a video returning detailed StreamResult object."""
        ffmpeg_bin = self.get_ffmpeg_binary_path()
        if not ffmpeg_bin:
            return StreamResult(success=False, error="FFmpeg binary not found")

        direct_url = self.resolve_stream_url(input_source)
        if not direct_url:
            logger.error(f"Skipping '{video_title}' – no playable stream URL available.")
            return StreamResult(success=False, error="Could not resolve stream URL")

        logger.info(f"Preparing stream for: '{video_title}'")

        if self.is_simulation:
            sim_time = min(duration_limit or 10, 10)
            logger.info(f"[Dry Run / Simulation] Streaming '{video_title}' for {sim_time} seconds...")
            time.sleep(sim_time)
            logger.info(f"[Dry Run / Simulation] Finished streaming '{video_title}'.")
            return StreamResult(success=True, duration=float(sim_time), resolved_url=direct_url)

        if self.session.is_alive:
            return self._feed_persistent(ffmpeg_bin, direct_url, video_title, duration_limit)

        return self._stream_standalone(ffmpeg_bin, direct_url, duration_limit, block)

    def _feed_persistent(
        self,
        ffmpeg_bin: str,
        direct_url: str,
        video_title: str,
        duration_limit: Optional[int],
    ) -> StreamResult:
        """Sub-method for feeding video into persistent stream session."""
        logger.info(f"Feeding '{video_title}' into persistent MPEG-TS stream...")
        cmd = self.command_builder.build_feeder_command(ffmpeg_bin, direct_url, duration_limit)
        try:
            feeder_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )

            buf_size = 64 * 1024
            while True:
                data = feeder_proc.stdout.read(buf_size) if feeder_proc.stdout else None
                if not data:
                    break
                if not self.session.write_chunk(data):
                    break

            feeder_proc.wait()
            logger.info(f"Finished feeding '{video_title}' to MPEG-TS stream.")
            return StreamResult(success=True, resolved_url=direct_url)
        except (subprocess.SubprocessError, OSError) as e:
            logger.error(f"Error feeding stream: {e}")
            return StreamResult(success=False, error=str(e), resolved_url=direct_url)

    def _stream_standalone(
        self,
        ffmpeg_bin: str,
        direct_url: str,
        duration_limit: Optional[int],
        block: bool,
    ) -> StreamResult:
        """Sub-method for launching standalone FLV/RTMP stream process."""
        logger.warning("Persistent stream stdin unavailable. Launching standalone RTMP stream...")
        target_rtmp = self.target.get_rtmp_url(self.stream_key)
        cmd = self.command_builder.build_standalone_command(
            ffmpeg_bin, direct_url, target_rtmp, duration_limit
        )
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            exit_code = None
            if block:
                exit_code = proc.wait()
            return StreamResult(
                success=True,
                resolved_url=direct_url,
                exit_code=exit_code,
            )
        except (subprocess.SubprocessError, OSError) as e:
            logger.error(f"Standalone streaming error: {e}")
            return StreamResult(success=False, error=str(e), resolved_url=direct_url)
