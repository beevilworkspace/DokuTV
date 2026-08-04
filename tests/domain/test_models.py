import unittest
from dokutv.domain import Video, PlaySlot, ChannelSchedule, InvalidVideoError, ScheduleError


class TestDomainModels(unittest.TestCase):

    def test_video_creation_and_methods(self):
        video = Video(
            id="v1",
            title="Cosmos",
            duration_seconds=3665,
            license="CC",
            description="Space doc",
            youtube_url="https://youtube.com/watch?v=v1",
        )
        self.assertEqual(video.formatted_duration(), "01:01:05")
        
        data = video.to_dict()
        self.assertEqual(data["id"], "v1")
        reconstructed = Video.from_dict(data)
        self.assertEqual(reconstructed.title, "Cosmos")

    def test_video_validation_rules(self):
        with self.assertRaises(InvalidVideoError):
            Video(id="", title="Valid Title")

        with self.assertRaises(InvalidVideoError):
            Video(id="v1", title="", duration_seconds=100)

        with self.assertRaises(InvalidVideoError):
            Video(id="v1", title="Valid", duration_seconds=-5)

    def test_play_slot_and_schedule_aggregate(self):
        schedule = ChannelSchedule(channel_name="DokuTV_EN")
        self.assertTrue(schedule.is_empty)

        slot = PlaySlot(
            slot_index=0,
            video_id="v1",
            title="Cosmos",
            youtube_url="http://v1",
            start_time="12:00",
            end_time="13:00",
            duration_seconds=3600,
        )
        self.assertEqual(slot.formatted_duration(), "60 min")

        schedule.add_slot(slot)
        self.assertFalse(schedule.is_empty)
        self.assertEqual(schedule.slot_count, 1)
        self.assertEqual(schedule.total_duration_seconds, 3600)

        schedule.clear()
        self.assertTrue(schedule.is_empty)


if __name__ == "__main__":
    unittest.main()
