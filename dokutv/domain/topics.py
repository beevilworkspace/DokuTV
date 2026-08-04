"""
Domain Layer - Broad Documentary Search Topics Pool.
Easily expandable list of broad, diverse documentary search queries.
"""

import random
from typing import List

DOCUMENTARY_TOPICS: List[str] = [
    # Animals & Wildlife
    "wildlife full documentary narrated",
    "animals nature full documentary narrated",
    "predators hunting full documentary",
    "african safari full documentary narrated",
    "ocean animals full documentary narrated",

    # Space & Universe
    "space exploration full documentary narrated",
    "astronomy universe full documentary",
    "NASA space mission full documentary",
    "black holes explained full documentary",
    "galaxies cosmos full documentary narrated",

    # Nature & Science
    "nature science full documentary narrated",
    "rainforest ecosystem full documentary",
    "climate change full documentary narrated",
    "volcanoes geology full documentary narrated",
    "evolution biology full documentary",

    # Deep Sea & Oceans
    "deep sea exploration full documentary narrated",
    "marine biology full documentary",
    "coral reef ecosystem full documentary narrated",
    "underwater world full documentary narrated",

    # History & Archaeology
    "ancient history full documentary narrated",
    "ancient civilization full documentary",
    "archaeology discovery full documentary narrated",
    "world war history full documentary narrated",
    "roman empire full documentary",

    # Physics & Science
    "physics explained full documentary narrated",
    "quantum mechanics full documentary",
    "science universe full documentary narrated",
    "engineering megastructures full documentary",

    # Technology
    "technology innovation full documentary narrated",
    "artificial intelligence full documentary",
    "future technology full documentary narrated",
]

def get_random_topic() -> str:
    """Return a randomly chosen documentary search topic from the pool."""
    return random.choice(DOCUMENTARY_TOPICS)
