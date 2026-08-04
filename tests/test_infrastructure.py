"""
Backward compatibility re-export wrapper.
Tests have been reorganized into tests/infrastructure/
"""
from tests.infrastructure.test_env_loader import *
from tests.infrastructure.test_app_config import *
from tests.infrastructure.test_logging import *

if __name__ == "__main__":
    import unittest
    unittest.main()
