import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from dokutv.domain.models import Video
from dokutv.adapters.youtube_collector import (
    YouTubeCollectorConfig,
    FallbackPlaylistStore,
    YouTubeApiClient,
    YouTubeCollectorAdapter,
)


class TestYouTubeCollectorAdapter(unittest.TestCase):

    def test_fallback_playlist_store_loading(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_playlist.json"
            sample_data = [
                {
                    "id": "sample1",
                    "title": "Sample Doc",
                    "duration_seconds": 1800,
                    "license": "CC",
                    "description": "Test doc",
                    "youtube_url": "https://youtube.com/watch?v=sample1",
                }
            ]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f)

            store = FallbackPlaylistStore(file_path)
            videos = store.load_curated_videos()
            self.assertEqual(len(videos), 1)
            self.assertEqual(videos[0].id, "sample1")

    def test_api_client_key_validation(self):
        invalid_config = YouTubeCollectorConfig(api_key="AIzaSyYourActualKeyHere")
        invalid_client = YouTubeApiClient(invalid_config)
        self.assertFalse(invalid_client.is_api_key_valid())

        valid_config = YouTubeCollectorConfig(api_key="AIzaSyRealApiKey1234567")
        valid_client = YouTubeApiClient(valid_config)
        self.assertTrue(valid_client.is_api_key_valid())

    def test_collector_adapter_candidate_selection_and_exclusion(self):
        config = YouTubeCollectorConfig(api_key="")
        mock_fallback = MagicMock(spec=FallbackPlaylistStore)
        v1 = Video(id="vid1", title="Doc 1", duration_seconds=100, license="CC", description="", youtube_url="http://v1")
        v2 = Video(id="vid2", title="Doc 2", duration_seconds=200, license="CC", description="", youtube_url="http://v2")
        mock_fallback.load_curated_videos.return_value = [v1, v2]

        adapter = YouTubeCollectorAdapter(
            config=config,
            fallback_store=mock_fallback,
        )

        next_vid = adapter.get_next_video(query="documentary", exclude_ids=["vid1"])
        self.assertEqual(next_vid.id, "vid2")


if __name__ == "__main__":
    unittest.main()
