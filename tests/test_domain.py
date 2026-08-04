import unittest
from dokutv.domain.models import Video, PlaySlot

class TestDomainEntities(unittest.TestCase):
    def test_video_entity(self):
        video = Video(id="v1", title="Test Doc", duration_seconds=3600)
        self.assertEqual(video.id, "v1")
        self.assertEqual(video.title, "Test Doc")
        self.assertEqual(video.duration_seconds, 3600)

    def test_play_slot_entity(self):
        slot = PlaySlot(
            slot_index=1,
            video_id="v1",
            title="Test Doc",
            youtube_url="https://youtube.com/watch?v=v1",
            start_time="2026-08-03T12:00:00",
            end_time="2026-08-03T13:00:00"
        )
        self.assertEqual(slot.slot_index, 1)
        self.assertEqual(slot.video_id, "v1")

if __name__ == "__main__":
    unittest.main()
