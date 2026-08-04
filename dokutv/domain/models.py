"""
Domain Layer - Entities & Value Objects.
Pure domain models with ZERO external or framework dependencies.
Includes rich domain methods, boundary validation, and immutable helpers.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from dokutv.domain.exceptions import InvalidVideoError, ScheduleError


@dataclass
class Video:
    """Core domain entity representing a documentary video."""
    id: str
    title: str
    duration_seconds: int = 3600
    license: str = "creativeCommon"
    description: str = ""
    youtube_url: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidVideoError("Video ID cannot be empty.")
        if not self.title:
            raise InvalidVideoError("Video title cannot be empty.")
        if self.duration_seconds <= 0:
            raise InvalidVideoError("Video duration_seconds must be positive.")

    def formatted_duration(self) -> str:
        """Return human-readable duration (HH:MM:SS or MM:SS)."""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Video to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "duration_seconds": self.duration_seconds,
            "license": self.license,
            "description": self.description,
            "youtube_url": self.youtube_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Video":
        """Instantiate Video from dictionary data."""
        return cls(
            id=data["id"],
            title=data["title"],
            duration_seconds=int(data.get("duration_seconds", 3600)),
            license=data.get("license", "creativeCommon"),
            description=data.get("description", ""),
            youtube_url=data.get("youtube_url", ""),
        )


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

    def __post_init__(self) -> None:
        if self.slot_index < 0:
            raise ScheduleError("PlaySlot slot_index cannot be negative.")
        if not self.video_id:
            raise ScheduleError("PlaySlot video_id cannot be empty.")

    def formatted_duration(self) -> str:
        """Return human-readable slot duration."""
        minutes = self.duration_seconds // 60
        return f"{minutes} min"


@dataclass
class ChannelSchedule:
    """Core domain aggregate root representing a channel broadcast schedule."""
    channel_name: str
    slots: List[PlaySlot] = field(default_factory=list)

    def add_slot(self, slot: PlaySlot) -> None:
        """Add a PlaySlot to the channel schedule."""
        self.slots.append(slot)

    def clear(self) -> None:
        """Clear all PlaySlots from the schedule."""
        self.slots.clear()

    @property
    def slot_count(self) -> int:
        """Return number of slots in the schedule."""
        return len(self.slots)

    @property
    def total_duration_seconds(self) -> int:
        """Calculate total duration of all scheduled slots in seconds."""
        return sum(slot.duration_seconds for slot in self.slots)

    @property
    def is_empty(self) -> bool:
        """Check if schedule contains no slots."""
        return len(self.slots) == 0
