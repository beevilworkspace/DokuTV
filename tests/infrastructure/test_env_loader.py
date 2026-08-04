import os
import tempfile
import unittest
from pathlib import Path

from dokutv.infrastructure import load_env, EnvironmentLoader


class TestEnvironmentLoader(unittest.TestCase):

    def test_environment_loader_from_custom_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env.test"
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("TEST_KEY_DOKUTV=hello_world\n")

            loader = EnvironmentLoader(default_file=str(env_file))
            loaded = loader.load(env_file=env_file)
            self.assertTrue(loaded)
            self.assertEqual(os.getenv("TEST_KEY_DOKUTV"), "hello_world")

    def test_load_env_helper(self):
        load_env()
        # Ensure helper runs without throwing exceptions


if __name__ == "__main__":
    unittest.main()
