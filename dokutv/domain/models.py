"""
Domain Layer - Entities & Value Objects.
Pure domain models with ZERO external or framework dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Video:
    """Core domain entity representing a documentary video."""
    id: str
    title: str
    duration_seconds: int = 3600
    license: str = "creativeCommon"
    description: str = ""
    youtube_url: str = ""

@dataclass
class PlaySlot:
    """Core domain entity representing a scheduled broadcast slot."""
    slot_index: int
    video_id: str
    title: str
    youtube_url: str
    start_time: str
    end_time: str
    duration_seconds: int = 3600

@dataclass
class ChannelSchedule:
    """Core domain aggregate representing a channel schedule."""
    channel_name: str
    slots: List[PlaySlot] = field(default_factory=list)
