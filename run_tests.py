"""
Test suite runner.
"""
import unittest
import sys

if __name__ == '__main__':
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(not result.wasSuccessful())
