"""
FFmpeg command builder component.
Centralizes command-line argument creation for feeder, persistent RTMP, and standalone streams.
"""

from typing import List, Optional
from dokutv.adapters.streaming.config import StreamingConfig


class FFmpegCommandBuilder:
    """Builds FFmpeg command argument lists."""

    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()

    def get_video_options(self) -> List[str]:
        """Video encoding options block."""
        return [
            "-c:v", "libx264",
            "-preset", self.config.video_preset,
            "-maxrate", self.config.video_maxrate,
            "-bufsize", self.config.buffer_size,
            "-pix_fmt", self.config.pixel_format,
            "-g", str(self.config.gop_size),
        ]

    def get_audio_options(self) -> List[str]:
        """Audio encoding options block."""
        return [
            "-c:a", "aac",
            "-b:a", self.config.audio_bitrate,
            "-ar", self.config.audio_sample_rate,
        ]

    def build_persistent_rtmp_command(self, ffmpeg_bin: str, target_rtmp_url: str) -> List[str]:
        """Build command for persistent RTMP stream process reading MPEG-TS stdin."""
        return [
            ffmpeg_bin,
            "-re",
            "-f", "mpegts",
            "-i", "pipe:0",
            "-c:v", "copy",
            "-c:a", "copy",
            "-f", "flv",
            target_rtmp_url,
        ]

    def build_feeder_command(
        self,
        ffmpeg_bin: str,
        input_source: str,
        audio_source: Optional[str] = None,
        duration_limit: Optional[int] = None,
    ) -> List[str]:
        """Build command to decode input_source (and optional audio_source) into MPEG-TS stdout stream."""
        cmd = [ffmpeg_bin, "-re"]
        if duration_limit:
            cmd.extend(["-t", str(duration_limit)])

        cmd.extend(["-i", input_source])
        if audio_source:
            cmd.extend(["-i", audio_source])
            cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])

        cmd.extend(self.get_video_options())
        cmd.extend(self.get_audio_options())
        cmd.extend(["-f", "mpegts", "pipe:1"])
        return cmd

    def build_standalone_command(
        self,
        ffmpeg_bin: str,
        input_source: str,
        target_rtmp_url: str,
        audio_source: Optional[str] = None,
        duration_limit: Optional[int] = None,
    ) -> List[str]:
        """Build command for standalone FLV/RTMP stream process."""
        cmd = [ffmpeg_bin, "-re"]
        if duration_limit:
            cmd.extend(["-t", str(duration_limit)])

        cmd.extend(["-i", input_source])
        if audio_source:
            cmd.extend(["-i", audio_source])
            cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])

        cmd.extend(self.get_video_options())
        cmd.extend(self.get_audio_options())
        cmd.extend(["-f", "flv", target_rtmp_url])
        return cmd
