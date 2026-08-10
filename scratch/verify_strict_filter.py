import unittest
from tests.test_strict_documentary_filter import TestStrictDocumentaryFilter
from tests.test_follow_overlay import TestFollowOverlayDomainModel, TestFollowOverlayTemplateRenderer

def run():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStrictDocumentaryFilter))
    suite.addTest(unittest.makeSuite(TestFollowOverlayDomainModel))
    suite.addTest(unittest.makeSuite(TestFollowOverlayTemplateRenderer))
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if res.wasSuccessful():
        print("SUCCESS: All tests passed!")
    else:
        print("FAILURE: Tests failed.")

if __name__ == "__main__":
    run()
