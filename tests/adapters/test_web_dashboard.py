import json
import urllib.request
import unittest
from unittest.mock import MagicMock
from dokutv.adapters.web_dashboard import WebDashboardAdapter


class TestWebDashboardAdapter(unittest.TestCase):

    def setUp(self):
        self.mock_engine = MagicMock()
        self.mock_engine.get_status.return_value = {
            "channel_name": "TestChannel",
            "is_running": True,
            "current_video": {"title": "Test Documentary", "duration_seconds": 1800},
            "history_count": 1,
        }
        self.mock_engine.get_history.return_value = []
        self.mock_engine.skip_current_video.return_value = True

        self.adapter = WebDashboardAdapter(engine=self.mock_engine, port=8888)
        self.adapter.start()

    def tearDown(self):
        self.adapter.stop()

    def test_dashboard_html_page(self):
        url = "http://localhost:8888/"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("DokuTV", content)
            self.assertIn("Video überspringen", content)

    def test_api_status_endpoint(self):
        url = "http://localhost:8888/api/status"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["channel_name"], "TestChannel")
            self.assertEqual(data["current_video"]["title"], "Test Documentary")

    def test_api_skip_endpoint(self):
        url = "http://localhost:8888/api/skip"
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data["success"])
            self.mock_engine.skip_current_video.assert_called_once()


if __name__ == "__main__":
    unittest.main()
