"""
FFmpeg binary locator component.
Locates FFmpeg executable across local workspace, imageio_ffmpeg, or PATH.
"""

import os
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FFmpegBinaryLocator:
    """Locates the FFmpeg binary executable."""

    def find(self) -> Optional[str]:
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

        logger.error("[FEHLER] 'ffmpeg' wurde auf Ihrem System nicht gefunden!")
        return None
