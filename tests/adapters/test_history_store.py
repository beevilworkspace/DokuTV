import os
import shutil
import tempfile
import unittest
from dokutv.domain.models import PlayHistoryEntry
from dokutv.adapters.history_store import JsonHistoryStoreAdapter


class TestJsonHistoryStoreAdapter(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.test_dir, "sub_dir", "history.json")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_add_and_get_history(self):
        adapter = JsonHistoryStoreAdapter(file_path=self.file_path)
        self.assertEqual(adapter.get_history(), [])

        entry1 = PlayHistoryEntry(
            video_id="vid1",
            title="Doku 1",
            played_at="2026-08-10T06:00:00Z",
            duration_seconds=1800,
            topic="nature",
            youtube_url="https://youtube.com/watch?v=vid1",
            license="creativeCommon",
            status="played",
        )
        entry2 = PlayHistoryEntry(
            video_id="vid2",
            title="Doku 2",
            played_at="2026-08-10T07:00:00Z",
            duration_seconds=3600,
            topic="science",
            youtube_url="https://youtube.com/watch?v=vid2",
            license="creativeCommon",
            status="played",
        )

        adapter.add_entry(entry1)
        adapter.add_entry(entry2)

        history = adapter.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].video_id, "vid1")
        self.assertEqual(history[0].title, "Doku 1")
        self.assertEqual(history[1].video_id, "vid2")
        self.assertEqual(history[1].title, "Doku 2")

    def test_clear_history(self):
        adapter = JsonHistoryStoreAdapter(file_path=self.file_path)
        entry = PlayHistoryEntry(
            video_id="vid1",
            title="Doku 1",
            played_at="2026-08-10T06:00:00Z",
        )
        adapter.add_entry(entry)
        self.assertEqual(len(adapter.get_history()), 1)

        adapter.clear_history()
        self.assertEqual(adapter.get_history(), [])

    def test_corrupted_file_handling(self):
        adapter = JsonHistoryStoreAdapter(file_path=self.file_path)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("INVALID JSON CONTENT")

        # Reading corrupted file should return empty list without crashing
        self.assertEqual(adapter.get_history(), [])

        # Adding entry should overwrite invalid JSON safely
        entry = PlayHistoryEntry(
            video_id="vid_new",
            title="New Doku",
            played_at="2026-08-10T08:00:00Z",
        )
        adapter.add_entry(entry)
        history = adapter.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].video_id, "vid_new")


if __name__ == "__main__":
    unittest.main()
