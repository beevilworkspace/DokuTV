import unittest
from dokutv.adapters import YouTubeCollectorAdapter

class TestYouTubeCollectorAdapter(unittest.TestCase):
    def test_curated_fallback(self):
        collector = YouTubeCollectorAdapter(api_key="AIzaSyYourActualKeyPlaceholder")
        docs = collector.search_cc_documentaries(query="test", max_results=5)
        self.assertTrue(len(docs) > 0)
        self.assertIsNotNone(docs[0].youtube_url)

if __name__ == "__main__":
    unittest.main()


