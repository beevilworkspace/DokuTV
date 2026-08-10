import unittest
from unittest.mock import MagicMock

from dokutv.domain.services import TwitchTitleFormatter, TitleFormatter


class TestDomainServices(unittest.TestCase):

    def test_title_formatter_with_explicit_prefix_and_suffix(self):
        formatter = TwitchTitleFormatter(
            title_prefix="🔴 24/7 Doku:",
            title_suffix="| DokuTV_EN",
        )
        result = formatter.format_title("Wonders of the Universe")
        self.assertEqual(result, "🔴 24/7 Doku: Wonders of the Universe | DokuTV_EN")

    def test_title_formatter_with_config_object(self):
        mock_config = MagicMock()
        mock_config.title_prefix = "[LIVE]"
        mock_config.title_suffix = "(EN)"

        formatter = TitleFormatter(config=mock_config)
        result = formatter.format_title("Nature Documentary")
        self.assertEqual(result, "[LIVE] Nature Documentary (EN)")

    def test_title_formatter_without_prefix_or_suffix(self):
        formatter = TitleFormatter()
        result = formatter.format_title("Simple Video Title")
        self.assertEqual(result, "Simple Video Title")


    def test_title_formatter_html_unescape(self):
        formatter = TwitchTitleFormatter(
            title_prefix="🔴 24/7 Doku:",
            title_suffix="| DokuTV_EN",
        )
        raw_title = "Secrets of the Octopus: the Ocean&#39;s Masterminds &amp; More"
        result = formatter.format_title(raw_title)
        self.assertEqual(result, "🔴 24/7 Doku: Secrets of the Octopus: the Ocean's Masterminds & More | DokuTV_EN")


if __name__ == "__main__":
    unittest.main()

