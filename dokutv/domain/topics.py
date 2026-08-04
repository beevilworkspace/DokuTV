"""
Domain Layer - Broad Documentary Search Topics Pool.
Structured topic categories and TopicProvider domain service.
"""

import random
from enum import Enum, auto
from typing import List, Dict, Optional


class TopicCategory(Enum):
    """Broad documentary topic categories."""
    WILDLIFE = "Wildlife"
    SPACE = "Space"
    NATURE_SCIENCE = "Nature & Science"
    DEEP_SEA = "Deep Sea"
    HISTORY = "History"
    PHYSICS = "Physics"
    TECHNOLOGY = "Technology"


CATEGORY_TOPICS_MAP: Dict[TopicCategory, List[str]] = {
    TopicCategory.WILDLIFE: [
        "wildlife full documentary narrated",
        "animals nature full documentary narrated",
        "predators hunting full documentary",
        "african safari full documentary narrated",
        "ocean animals full documentary narrated",
    ],
    TopicCategory.SPACE: [
        "space exploration full documentary narrated",
        "astronomy universe full documentary",
        "NASA space mission full documentary",
        "black holes explained full documentary",
        "galaxies cosmos full documentary narrated",
    ],
    TopicCategory.NATURE_SCIENCE: [
        "nature science full documentary narrated",
        "rainforest ecosystem full documentary",
        "climate change full documentary narrated",
        "volcanoes geology full documentary narrated",
        "evolution biology full documentary",
    ],
    TopicCategory.DEEP_SEA: [
        "deep sea exploration full documentary narrated",
        "marine biology full documentary",
        "coral reef ecosystem full documentary narrated",
        "underwater world full documentary narrated",
    ],
    TopicCategory.HISTORY: [
        "ancient history full documentary narrated",
        "ancient civilization full documentary",
        "archaeology discovery full documentary narrated",
        "world war history full documentary narrated",
        "roman empire full documentary",
    ],
    TopicCategory.PHYSICS: [
        "physics explained full documentary narrated",
        "quantum mechanics full documentary",
        "science universe full documentary narrated",
        "engineering megastructures full documentary",
    ],
    TopicCategory.TECHNOLOGY: [
        "technology innovation full documentary narrated",
        "artificial intelligence full documentary",
        "future technology full documentary narrated",
    ],
}

# Flat list of all documentary topics for backward compatibility
DOCUMENTARY_TOPICS: List[str] = [
    topic for topic_list in CATEGORY_TOPICS_MAP.values() for topic in topic_list
]


class TopicProvider:
    """Domain service for retrieving documentary search topics."""

    def __init__(self, category_map: Optional[Dict[TopicCategory, List[str]]] = None):
        self.category_map = category_map or CATEGORY_TOPICS_MAP

    def get_topics(self, category: Optional[TopicCategory] = None) -> List[str]:
        """Get all topics, optionally filtered by TopicCategory."""
        if category and category in self.category_map:
            return list(self.category_map[category])
        return [t for topic_list in self.category_map.values() for t in topic_list]

    def get_random_topic(self, category: Optional[TopicCategory] = None) -> str:
        """Return a randomly chosen documentary topic, optionally filtered by category."""
        topics = self.get_topics(category)
        return random.choice(topics)


# Global default instance
_DEFAULT_TOPIC_PROVIDER = TopicProvider()


def get_random_topic(category: Optional[TopicCategory] = None) -> str:
    """Backward-compatible wrapper returning a random documentary topic."""
    return _DEFAULT_TOPIC_PROVIDER.get_random_topic(category)
