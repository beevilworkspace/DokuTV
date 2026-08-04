"""
Backward compatibility re-export wrapper.
Tests have been reorganized into tests/application/
"""
from tests.application.test_engine import *

if __name__ == "__main__":
    import unittest
    unittest.main()
