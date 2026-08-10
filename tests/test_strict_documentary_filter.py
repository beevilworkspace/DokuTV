"""
Unit & Integration Tests for Strict Documentary Filtering Strategy.
Tests category enforcement, minimum duration checks, rejection of non-documentary category IDs (e.g. Gaming),
and zero fallback to uncategorized searches.
"""

import unittest
from unittest.mock import MagicMock, patch

from dokutv.domain.models import Video
from dokutv.adapters.collector.youtube_api_client import (
    YouTubeApiClient,
    ALLOWED_DOCUMENTARY_CATEGORIES,
    MINIMUM_DOCUMENTARY_DURATION_SECONDS,
)
from dokutv.adapters.collector.collector_config import YouTubeCollectorConfig
from dokutv.adapters.collector.youtube_collector_adapter import YouTubeCollectorAdapter


class TestStrictDocumentaryFilter(unittest.TestCase):
    """Tests for strict category isolation and documentary filtering."""

    def test_allowed_categories_const(self):
        self.assertIn("35", ALLOWED_DOCUMENTARY_CATEGORIES)  # Documentary / Film
        self.assertIn("28", ALLOWED_DOCUMENTARY_CATEGORIES)  # Science & Tech
        self.assertIn("27", ALLOWED_DOCUMENTARY_CATEGORIES)  # Education
        self.assertNotIn("20", ALLOWED_DOCUMENTARY_CATEGORIES)  # Gaming
        self.assertNotIn("24", ALLOWED_DOCUMENTARY_CATEGORIES)  # Entertainment

    @patch("dokutv.adapters.collector.youtube_api_client.urllib.request.urlopen")
    def test_search_videos_rejects_non_documentary_category_id(self, mock_urlopen):
        # Mock search response returning a video with categoryId = 20 (Gaming)
        search_response = json_dumps({
            "items": [
                {
                    "id": {"videoId": "gaming123"},
                    "snippet": {
                        "title": "far cry primal gameplay",
                        "description": "gaming video",
                        "categoryId": "20"
                    }
                }
            ]
        })

        details_response = json_dumps({
            "items": [
                {
                    "id": "gaming123",
                    "snippet": {"categoryId": "20"},
                    "contentDetails": {"duration": "PT1H00M00S"}
                }
            ]
        })

        mock_resp_search = MagicMock()
        mock_resp_search.read.return_value = search_response.encode("utf-8")
        mock_resp_search.__enter__.return_value = mock_resp_search

        mock_resp_details = MagicMock()
        mock_resp_details.read.return_value = details_response.encode("utf-8")
        mock_resp_details.__enter__.return_value = mock_resp_details

        mock_urlopen.side_effect = [mock_resp_search, mock_resp_details, mock_resp_search, mock_resp_search]

        config = YouTubeCollectorConfig(api_key="AIzaSyTestKeyValid123456789")
        client = YouTubeApiClient(config)
        results = client.search_videos("glaciers ice age")

        # The gaming video (cat_id 20) MUST be rejected!
        self.assertEqual(len(results), 0)

    @patch("dokutv.adapters.collector.youtube_api_client.urllib.request.urlopen")
    def test_search_videos_rejects_short_videos(self, mock_urlopen):
        search_response = json_dumps({
            "items": [
                {
                    "id": {"videoId": "short123"},
                    "snippet": {
                        "title": "Short Clip",
                        "description": "Doc clip",
                        "categoryId": "35"
                    }
                }
            ]
        })

        # Duration = 200s (< 600s minimum)
        details_response = json_dumps({
            "items": [
                {
                    "id": "short123",
                    "snippet": {"categoryId": "35"},
                    "contentDetails": {"duration": "PT03M20S"}
                }
            ]
        })

        mock_resp_search = MagicMock()
        mock_resp_search.read.return_value = search_response.encode("utf-8")
        mock_resp_search.__enter__.return_value = mock_resp_search

        mock_resp_details = MagicMock()
        mock_resp_details.read.return_value = details_response.encode("utf-8")
        mock_resp_details.__enter__.return_value = mock_resp_details

        mock_urlopen.side_effect = [mock_resp_search, mock_resp_details, mock_resp_search, mock_resp_search]

        config = YouTubeCollectorConfig(api_key="AIzaSyTestKeyValid123456789")
        client = YouTubeApiClient(config)
        results = client.search_videos("nature science")

        # Short clip MUST be rejected!
        self.assertEqual(len(results), 0)

    def test_trusted_channels_loading(self):
        adapter = YouTubeCollectorAdapter(api_key="AIzaSyTestKeyValid123456789")
        channels = adapter._load_trusted_channels()
        self.assertTrue(len(channels) > 0)
        channel_names = [c.get("name") for c in channels]
        self.assertIn("DW Documentary", channel_names)


def json_dumps(obj):
    import json
    return json.dumps(obj)


if __name__ == "__main__":
    unittest.main()
