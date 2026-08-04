"""
Backward compatibility re-export wrapper.
Tests have been reorganized into tests/domain/
"""
from tests.domain.test_models import *
from tests.domain.test_topics import *
from tests.domain.test_exceptions import *

if __name__ == "__main__":
    import unittest
    unittest.main()
