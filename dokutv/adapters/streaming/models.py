"""
Models and data transfer objects for streaming operations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StreamResult:
    """Detailed result status for video streaming operations."""
    success: bool
    error: Optional[str] = None
    duration: Optional[float] = None
    resolved_url: Optional[str] = None
    exit_code: Optional[int] = None
