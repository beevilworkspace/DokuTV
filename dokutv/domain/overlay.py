"""
Domain Layer - Follow Overlay Entities & Localization Config.
Pure domain models for Follow-Overlay settings, default texts, and multi-language support (i18n).
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

# Centralized multi-language dictionary for Follow-Overlay texts
OVERLAY_I18N: Dict[str, Dict[str, str]] = {
    "de": {
        "cta": "Gefällt dir der Content? Lass ein Follow da!",
        "btn": "💜 Kostenlos Folgen",
    },
    "en": {
        "cta": "Enjoying the content? Hit the follow button!",
        "btn": "💜 Follow for Free",
    },
    "es": {
        "cta": "¿Te gusta el contenido? ¡Deja un follow!",
        "btn": "💜 Seguir gratis",
    },
    "fr": {
        "cta": "Vous aimez le contenu ? Laissez un follow !",
        "btn": "💜 Suivre gratuitement",
    },
}

VALID_POSITIONS = {
    "bottom-left",
    "bottom-center",
    "bottom-right",
    "top-left",
    "top-right",
    "top-center",
}

DEFAULT_LANG = "de"
DEFAULT_USER = "DeinKanalName"
DEFAULT_COLOR = "9146FF"
DEFAULT_POS = "bottom-left"
DEFAULT_SCALE = 100


@dataclass
class FollowOverlayConfig:
    """Domain model representing Follow-Overlay settings and parameters."""

    user: str = DEFAULT_USER
    lang: str = DEFAULT_LANG
    cta: Optional[str] = None
    btn: Optional[str] = None
    color: str = DEFAULT_COLOR
    pos: str = DEFAULT_POS
    scale: int = DEFAULT_SCALE

    def __post_init__(self) -> None:
        # Normalize language key
        self.lang = (self.lang or DEFAULT_LANG).lower().strip()
        if self.lang not in OVERLAY_I18N:
            self.lang = DEFAULT_LANG

        # Normalize position
        if not self.pos or self.pos not in VALID_POSITIONS:
            self.pos = DEFAULT_POS

        # Normalize scale (clamped between 10% and 500%)
        try:
            self.scale = max(10, min(500, int(self.scale)))
        except (ValueError, TypeError):
            self.scale = DEFAULT_SCALE

        # Clean color hex string
        if self.color:
            self.color = self.color.lstrip("#").strip()
        if not self.color:
            self.color = DEFAULT_COLOR

        # Clean username
        if not self.user:
            self.user = DEFAULT_USER

    @property
    def formatted_user(self) -> str:
        """Ensure username starts with @ symbol."""
        user_str = self.user.strip()
        return user_str if user_str.startswith("@") else f"@{user_str}"

    @property
    def effective_cta(self) -> str:
        """Return custom CTA string if specified, or localized default."""
        if self.cta and self.cta.strip():
            return self.cta.strip()
        lang_data = OVERLAY_I18N.get(self.lang) or OVERLAY_I18N[DEFAULT_LANG]
        return lang_data["cta"]

    @property
    def effective_btn(self) -> str:
        """Return custom button text if specified, or localized default."""
        if self.btn and self.btn.strip():
            return self.btn.strip()
        lang_data = OVERLAY_I18N.get(self.lang) or OVERLAY_I18N[DEFAULT_LANG]
        return lang_data["btn"]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration into dynamic JSON-serializable dictionary."""
        return {
            "user": self.formatted_user,
            "cta": self.effective_cta,
            "btn": self.effective_btn,
            "color": self.color,
            "pos": self.pos,
            "scale": self.scale,
            "lang": self.lang,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FollowOverlayConfig":
        """Factory method to build FollowOverlayConfig from a dictionary or query params."""
        return cls(
            user=str(data.get("user", DEFAULT_USER)),
            lang=str(data.get("lang", DEFAULT_LANG)),
            cta=data.get("cta"),
            btn=data.get("btn"),
            color=str(data.get("color", DEFAULT_COLOR)),
            pos=str(data.get("pos", DEFAULT_POS)),
            scale=data.get("scale", DEFAULT_SCALE),
        )
