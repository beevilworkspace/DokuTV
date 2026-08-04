import logging
import unittest
from dokutv.infrastructure import setup_logging


class TestLoggingConfig(unittest.TestCase):

    def test_setup_logging(self):
        setup_logging(level=logging.DEBUG)
        root = logging.getLogger()
        self.assertEqual(root.level, logging.DEBUG)
        self.assertGreater(len(root.handlers), 0)


if __name__ == "__main__":
    unittest.main()
