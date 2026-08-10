import json
import os
import re
import random
from enum import Enum
from typing import List, Dict, Optional, Set

DEFAULT_BLACKLISTED_KEYWORDS: List[str] = [
    "sleep",
    "sleeping",
    "chill",
    "chilled",
    "relax",
    "relaxing",
    "relaxation",
    "ambient",
    "music",
    "lofi",
    "meditation",
    "lullaby",
    "calm",
    "calming",
    "study",
    "studying",
    "screensaver",
    "asmr",
    "white noise",
    "rain sounds",
    "soundtrack",
    "soothing",
    "deep sleep",
    "stress relief",
    "nature sounds",
    "trailer",
    "official trailer",
    "teaser",
    "reaction",
    "review",
    "gameplay",
    "walkthrough",
    "gaming",
    "podcast",
]


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
        "apex predators wild animals full documentary narrated",
        "big cats lions tigers hunting full documentary narrated",
        "ocean giants whales sharks marine life full documentary",
        "african safari wildlife predators full documentary narrated",
        "animal intelligence instinct species full documentary",
        "extreme wildlife survival strategies full documentary narrated",
        "polar predators arctic wolves bears full documentary",
        "reptiles snakes crocodiles wild nature full documentary",
    ],
    TopicCategory.SPACE: [
        "James Webb space telescope discoveries full documentary narrated",
        "black holes event horizon astrophysics full documentary",
        "search for alien life exoplanets universe full documentary",
        "NASA space exploration missions history full documentary",
        "origin of the universe cosmos astronomy full documentary",
        "mars exploration rover mission space full documentary",
        "galaxies nebula stellar evolution astrophysics full documentary",
        "solar system planets moons discovery full documentary",
    ],
    TopicCategory.NATURE_SCIENCE: [
        "natural disasters supervolcanoes geology full documentary",
        "rainforest ecosystem biodiversity nature full documentary",
        "earth science climate forces nature full documentary narrated",
        "evolution species genetics biology full documentary",
        "plant intelligence fungal network nature full documentary",
        "extreme weather mega storms meteorology full documentary",
        "glaciers ice age earth history full documentary narrated",
    ],
    TopicCategory.DEEP_SEA: [
        "deep sea abyssal trench ocean exploration full documentary",
        "bioluminescent creatures deep ocean full documentary narrated",
        "hydrothermal vents abyssal ecosystem full documentary",
        "giant squid oceanic monsters deep sea full documentary",
        "marine oceanography underwater mysteries full documentary",
        "coral reef ecosystem oceanic life full documentary narrated",
    ],
    TopicCategory.HISTORY: [
        "ancient egypt pyramids pharaohs archaeology full documentary",
        "roman empire rise and fall ancient history full documentary",
        "ancient greece spartans mythology archaeology full documentary",
        "lost civilizations mayan inca megaliths full documentary",
        "world war 2 battle strategy military history full documentary",
        "medieval castles siege warfare history full documentary",
        "archaeological discoveries ancient artifacts full documentary",
        "cold war espionage secret missions history full documentary",
    ],
    TopicCategory.PHYSICS: [
        "quantum mechanics physics universe explained full documentary",
        "relativity time dilation astrophysics full documentary",
        "CERN particle physics Large Hadron Collider full documentary",
        "string theory multiverse theoretical physics full documentary",
        "engineering megastructures superstructures science full documentary",
        "mysteries of space time physics full documentary narrated",
    ],
    TopicCategory.TECHNOLOGY: [
        "artificial intelligence revolution machine learning full documentary",
        "quantum computing future computer science full documentary",
        "cybersecurity dark web digital technology full documentary",
        "future robotics automation technology full documentary",
        "spaceflight rocket engineering space tech full documentary",
        "renewable energy technology innovation full documentary",
    ],
}


# Flat list of all documentary topics for backward compatibility
DOCUMENTARY_TOPICS: List[str] = [
    topic for topic_list in CATEGORY_TOPICS_MAP.values() for topic in topic_list
]


class TopicProvider:
    """Domain service for retrieving documentary search topics and filtering unsuited content."""

    def __init__(self, json_path: Optional[str] = "data/search_topics.json"):
        self.category_map = dict(CATEGORY_TOPICS_MAP)
        self.blacklisted_keywords: Set[str] = set(DEFAULT_BLACKLISTED_KEYWORDS)

        if json_path and os.path.exists(json_path):
            self._load_from_json(json_path)

    def _load_from_json(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "blacklisted_keywords" in data:
                    self.blacklisted_keywords = {kw.lower() for kw in data["blacklisted_keywords"]}
                if "categories" in data and isinstance(data["categories"], dict):

                    cat_map_by_name = {cat.value: cat for cat in TopicCategory}
                    for cat_name, topics in data["categories"].items():
                        if cat_name in cat_map_by_name and isinstance(topics, list):
                            self.category_map[cat_map_by_name[cat_name]] = topics
        except Exception as e:
            pass

    def get_topics(self, category: Optional[TopicCategory] = None) -> List[str]:
        """Get all topics, optionally filtered by TopicCategory."""
        if category and category in self.category_map:
            return list(self.category_map[category])
        return [t for topic_list in self.category_map.values() for t in topic_list]

    def get_random_topic(self, category: Optional[TopicCategory] = None) -> str:
        """Return a randomly chosen documentary topic, optionally filtered by category."""
        topics = self.get_topics(category)
        return random.choice(topics)

    def is_valid_documentary(self, title: str, description: str = "") -> bool:
        """Check whether video title/description contains blacklisted sleep/chill/relaxing terms."""
        text = f"{title} {description}".lower()
        for kw in self.blacklisted_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                return False
        return True


# Global default instance
_DEFAULT_TOPIC_PROVIDER = TopicProvider()


def get_random_topic(category: Optional[TopicCategory] = None) -> str:
    """Backward-compatible wrapper returning a random documentary topic."""
    return _DEFAULT_TOPIC_PROVIDER.get_random_topic(category)


def is_valid_documentary(title: str, description: str = "") -> bool:
    """Check if title or description violates blacklisted keywords."""
    return _DEFAULT_TOPIC_PROVIDER.is_valid_documentary(title, description)

