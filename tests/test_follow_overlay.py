"""
Unit & Integration Tests for Follow-Overlay Feature.
Tests domain models, i18n localization, HTML template rendering, and HTTP endpoint handlers using standard unittest.
"""

import json
import unittest
from urllib.request import urlopen, Request

from dokutv.domain.overlay import (
    FollowOverlayConfig,
    OVERLAY_I18N,
    DEFAULT_LANG,
    DEFAULT_USER,
    DEFAULT_COLOR,
    DEFAULT_POS,
    DEFAULT_SCALE,
)
from dokutv.adapters.follow_overlay_template import render_follow_overlay
from dokutv.adapters.web_dashboard import WebDashboardAdapter


class TestFollowOverlayDomainModel(unittest.TestCase):
    """Test FollowOverlayConfig domain dataclass and localization logic."""

    def test_default_configuration(self):
        config = FollowOverlayConfig()
        self.assertEqual(config.formatted_user, "@DeinKanalName")
        self.assertEqual(config.lang, "de")
        self.assertEqual(config.effective_cta, "Gefällt dir der Content? Lass ein Follow da!")
        self.assertEqual(config.effective_btn, "💜 Kostenlos Folgen")
        self.assertEqual(config.color, "9146FF")
        self.assertEqual(config.pos, "bottom-left")
        self.assertEqual(config.scale, 100)

    def test_english_localization(self):
        config = FollowOverlayConfig(lang="en")
        self.assertEqual(config.effective_cta, "Enjoying the content? Hit the follow button!")
        self.assertEqual(config.effective_btn, "💜 Follow for Free")

    def test_spanish_localization(self):
        config = FollowOverlayConfig(lang="es")
        self.assertEqual(config.effective_cta, "¿Te gusta el contenido? ¡Deja un follow!")
        self.assertEqual(config.effective_btn, "💜 Seguir gratis")

    def test_custom_text_overrides(self):
        config = FollowOverlayConfig(
            cta="Einzigartige Dokumentation!",
            btn="🔔 Jetzt abonnieren"
        )
        self.assertEqual(config.effective_cta, "Einzigartige Dokumentation!")
        self.assertEqual(config.effective_btn, "🔔 Jetzt abonnieren")

    def test_invalid_language_fallback(self):
        config = FollowOverlayConfig(lang="invalid_lang")
        self.assertEqual(config.lang, DEFAULT_LANG)
        self.assertEqual(config.effective_cta, OVERLAY_I18N["de"]["cta"])

    def test_username_formatting(self):
        config1 = FollowOverlayConfig(user="MeinSender")
        self.assertEqual(config1.formatted_user, "@MeinSender")

        config2 = FollowOverlayConfig(user="@MeinSender")
        self.assertEqual(config2.formatted_user, "@MeinSender")

    def test_color_hex_formatting(self):
        config = FollowOverlayConfig(color="#FF0055")
        self.assertEqual(config.color, "FF0055")

    def test_position_fallback(self):
        config1 = FollowOverlayConfig(pos="top-right")
        self.assertEqual(config1.pos, "top-right")

        config2 = FollowOverlayConfig(pos="invalid_position")
        self.assertEqual(config2.pos, DEFAULT_POS)

    def test_scale_clamping(self):
        config_low = FollowOverlayConfig(scale=5)
        self.assertEqual(config_low.scale, 10)

        config_high = FollowOverlayConfig(scale=1000)
        self.assertEqual(config_high.scale, 500)

    def test_dict_serialization_and_deserialization(self):
        data = {
            "user": "CustomChannel",
            "lang": "en",
            "cta": "Check out our live stream!",
            "btn": "Follow Us",
            "color": "00FF88",
            "pos": "top-center",
            "scale": 120,
        }
        config = FollowOverlayConfig.from_dict(data)
        serialized = config.to_dict()

        self.assertEqual(serialized["user"], "@CustomChannel")
        self.assertEqual(serialized["lang"], "en")
        self.assertEqual(serialized["cta"], "Check out our live stream!")
        self.assertEqual(serialized["btn"], "Follow Us")
        self.assertEqual(serialized["color"], "00FF88")
        self.assertEqual(serialized["pos"], "top-center")
        self.assertEqual(serialized["scale"], 120)


class TestFollowOverlayTemplateRenderer(unittest.TestCase):
    """Test HTML rendering of follow overlay with dynamic config injection."""

    def test_render_follow_overlay_contains_injected_json(self):
        config = FollowOverlayConfig(
            user="DokuStreamer",
            lang="en",
            color="FF0055",
            pos="bottom-right",
            scale=110,
        )
        html = render_follow_overlay(config)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('lang="en"', html)
        self.assertIn("#FF0055", html)
        self.assertIn('"@DokuStreamer"', html)
        self.assertIn('"bottom-right"', html)
        self.assertIn('"Follow Overlay – DokuTV"', html)


class TestFollowOverlayHttpEndpoints(unittest.TestCase):
    """Test HTTP integration endpoints for overlay in WebDashboardAdapter."""

    def setUp(self):
        self.port = 8999
        self.adapter = WebDashboardAdapter(engine=None, port=self.port)
        self.adapter.start()

    def tearDown(self):
        self.adapter.stop()

    def test_get_follow_overlay_html(self):
        url = f"http://localhost:{self.port}/overlay/follow?user=TestChannel&lang=en&color=00F0FF"
        req = Request(url)
        with urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.headers.get("Content-Type"))
            content = resp.read().decode("utf-8")
            self.assertIn("TestChannel", content)
            self.assertIn("00F0FF", content)
            self.assertIn("Follow for Free", content)

    def test_get_follow_overlay_config_json(self):
        url = f"http://localhost:{self.port}/api/overlay/config?user=LiveSender&lang=de&pos=top-left"
        req = Request(url)
        with urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type"))
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["user"], "@LiveSender")
            self.assertEqual(data["lang"], "de")
            self.assertEqual(data["pos"], "top-left")
            self.assertEqual(data["cta"], "Gefällt dir der Content? Lass ein Follow da!")


if __name__ == "__main__":
    unittest.main()
