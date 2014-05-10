"""
Exercise the Website class to insure the methods operate
as expected.
"""

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary import website

class TestRecordSkinsTask(unittest.TestCase):
    """Run some tests."""

    def test_record_skins(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_skins()

if __name__ == '__main__':
    unittest.main()
