"""
Run tests on website class.
"""

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary import website


class test_website(unittest.TestCase):
    """Run some tests."""

    def setUp(self):
        pass

    def test_website_id(self):
        """ Test website ID method"""
        site = website.Website(18, 'WikiApiary', 'http://wikiapiary.com/w/api.url')
        self.assertEqual(site.get_id(), 18, "Site ID is not correct.")


if __name__ == '__main__':
    unittest.main()