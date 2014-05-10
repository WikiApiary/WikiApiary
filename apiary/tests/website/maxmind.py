"""
Exercise the Website class to insure the methods operate
as expected.
"""

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary import website

class TestMaxmindTask(unittest.TestCase):
    """Run some tests."""

    def test_maxmind_task(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_maxmind()

if __name__ == '__main__':
    unittest.main()
