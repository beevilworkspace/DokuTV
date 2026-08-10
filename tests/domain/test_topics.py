import unittest
from dokutv.domain import TopicCategory, TopicProvider, get_random_topic, DOCUMENTARY_TOPICS


class TestDomainTopics(unittest.TestCase):

    def test_topic_provider_all_topics(self):
        provider = TopicProvider()
        topics = provider.get_topics()
        self.assertEqual(len(topics), len(DOCUMENTARY_TOPICS))
        self.assertIn("James Webb space telescope discoveries full documentary narrated", topics)

    def test_topic_provider_category_filtering(self):
        provider = TopicProvider()
        space_topics = provider.get_topics(TopicCategory.SPACE)
        self.assertGreater(len(space_topics), 0)

        random_space_topic = provider.get_random_topic(TopicCategory.SPACE)
        self.assertIn(random_space_topic, space_topics)

    def test_global_random_topic_wrapper(self):
        topic = get_random_topic()
        self.assertIsInstance(topic, str)
        self.assertIn(topic, DOCUMENTARY_TOPICS)

    def test_is_valid_documentary_blacklist_filter(self):
        from dokutv.domain import is_valid_documentary

        # Valid documentary titles
        self.assertTrue(is_valid_documentary("Secrets of the Octopus: Ocean Masterminds"))
        self.assertTrue(is_valid_documentary("BBC Horizon: Space Exploration and Black Holes"))

        # Blacklisted titles (sleep, chill, relaxation, music, etc.)
        self.assertFalse(is_valid_documentary("8 Hours Deep Sleep Music for Relaxation"))
        self.assertFalse(is_valid_documentary("Chill Lofi Beats for Study and Meditation"))
        self.assertFalse(is_valid_documentary("Ambient Ocean Sounds for Sleeping"))


if __name__ == "__main__":
    unittest.main()

