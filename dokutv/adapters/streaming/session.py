"""
Persistent stream session lifecycle management.
Encapsulates background subprocess, pipe writes, health checks, and graceful termination.
"""

import subprocess
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class PersistentStreamSession:
    """Manages the lifecycle of a persistent FFmpeg streaming subprocess."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None

    @property
    def is_alive(self) -> bool:
        """Check if persistent FFmpeg process is running and stdin pipe is open."""
        return (
            self.process is not None
            and self.process.poll() is None
            and self.process.stdin is not None
        )

    def start(self, cmd: List[str]) -> bool:
        """Start persistent stream process with given command line."""
        try:
            logger.info(f"Initializing persistent stream process...")
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("✅ Persistent stream connected!")
            return True
        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            logger.error(f"Failed to start persistent RTMP stream: {e}")
            self.process = None
            return False

    def write_chunk(self, data: bytes) -> bool:
        """Write a data chunk to the persistent stream's stdin."""
        if not self.is_alive or not self.process.stdin:
            return False

        try:
            self.process.stdin.write(data)
            self.process.stdin.flush()
            return True
        except (BrokenPipeError, OSError) as write_err:
            logger.error(f"Persistent stream stdin write error: {write_err}")
            return False

    def stop(self, timeout: float = 3.0) -> None:
        """Close stdin and terminate the persistent stream process."""
        if not self.process:
            return

        logger.info("Closing persistent RTMP stream process...")
        try:
            if self.process.stdin:
                try:
                    self.process.stdin.close()
                except (BrokenPipeError, OSError):
                    pass
            self.process.terminate()
            self.process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            logger.warning(f"Error terminating persistent stream: {e}")
            if self.process:
                try:
                    self.process.kill()
                except OSError:
                    pass
        finally:
            self.process = None
            logger.info("Persistent RTMP stream closed.")
