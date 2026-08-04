import unittest

from dokutv.application.ports import (
    ContentCollectorPort,
    StreamerPort,
    PersistentStreamerPort,
    TwitchPort,
    ChannelManagementPort,
)
from tests.fakes import (
    FakeContentCollectorAdapter,
    FakeStreamerAdapter,
    FakeTwitchAdapter,
)


class TestApplicationPorts(unittest.TestCase):

    def test_fake_adapters_satisfy_ports(self):
        collector = FakeContentCollectorAdapter()
        streamer = FakeStreamerAdapter()
        twitch = FakeTwitchAdapter()

        self.assertIsInstance(collector, ContentCollectorPort)
        self.assertIsInstance(streamer, StreamerPort)
        self.assertIsInstance(twitch, TwitchPort)
        self.assertIsInstance(twitch, ChannelManagementPort)


if __name__ == "__main__":
    unittest.main()
