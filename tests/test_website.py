import os
import sys
import unittest
from ..apiary import website


class test_website(unittest.TestCase):

    def setUp(self):
        pass

    def test_website_id(self):
        site = website.Website(18, 'WikiApiary', 'http://wikiapiary.com/w/api.url')
        self.assertEqual(site.get_id(), 18, "Site ID is not correct.")


if __name__ == '__main__':
    unittest.main()
