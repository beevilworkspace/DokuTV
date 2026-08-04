import unittest
from dokutv.adapters import ScheduleRepositoryAdapter

class TestScheduleRepositoryAdapter(unittest.TestCase):
    def test_schedule_generation(self):
        repo = ScheduleRepositoryAdapter(playlist_file="non_existent.json")
        videos = repo.load_videos()
        schedule = repo.generate_30_day_schedule(videos)
        self.assertTrue(len(schedule) > 0)
        
        slot = repo.get_current_playing_slot(schedule)
        self.assertIsNotNone(slot)
        self.assertIsNotNone(slot.title)

if __name__ == "__main__":
    unittest.main()
