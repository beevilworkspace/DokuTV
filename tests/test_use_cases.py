import unittest
from dokutv.domain.models import Video, PlaySlot
from dokutv.application.use_cases import DiscoverContentUseCase, PlanScheduleUseCase

class MockCollectorAdapter:
    def search_cc_documentaries(self, query: str = "documentary", max_results: int = 30):
        return [Video(id="m1", title="Mock Doc 1")]
    def save_playlist_cache(self, videos, filepath="data/playlist_cache.json"):
        pass

class MockScheduleRepoAdapter:
    def load_videos(self):
        return [Video(id="m1", title="Mock Doc 1")]
    def generate_30_day_schedule(self, videos):
        return [PlaySlot(
            slot_index=1, video_id="m1", title="Mock Doc 1",
            youtube_url="https://youtube.com/watch?v=m1",
            start_time="2026-08-03T12:00:00", end_time="2026-08-03T13:00:00"
        )]
    def get_current_playing_slot(self, schedule):
        return schedule[0] if schedule else None
    def save_schedule(self, schedule, filepath="data/schedule_30_days.json"):
        pass

class TestUseCases(unittest.TestCase):
    def test_discover_content_use_case(self):
        use_case = DiscoverContentUseCase(collector_port=MockCollectorAdapter())
        videos = use_case.execute(query="nature")
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0].id, "m1")

    def test_plan_schedule_use_case(self):
        use_case = PlanScheduleUseCase(schedule_repo_port=MockScheduleRepoAdapter())
        schedule = use_case.execute()
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0].title, "Mock Doc 1")

if __name__ == "__main__":
    unittest.main()
