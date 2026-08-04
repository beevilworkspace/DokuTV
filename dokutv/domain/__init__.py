"""
Domain Layer Package
Pure domain models, value objects, domain services, and domain exceptions.
"""

from dokutv.domain.models import Video, PlaySlot, ChannelSchedule
from dokutv.domain.topics import (
    DOCUMENTARY_TOPICS,
    TopicCategory,
    TopicProvider,
    get_random_topic,
)
from dokutv.domain.exceptions import (
    DomainError,
    InvalidVideoError,
    ScheduleError,
)

__all__ = [
    "Video",
    "PlaySlot",
    "ChannelSchedule",
    "DOCUMENTARY_TOPICS",
    "TopicCategory",
    "TopicProvider",
    "get_random_topic",
    "DomainError",
    "InvalidVideoError",
    "ScheduleError",
]
