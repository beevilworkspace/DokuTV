"""
Backward compatibility re-export wrapper.
Tests have been reorganized into tests/adapters/
"""
from tests.adapters.test_history_store import *

if __name__ == "__main__":
    import unittest
    unittest.main()
