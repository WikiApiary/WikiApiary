"""
Exercise the Website class to insure the methods operate
as expected.
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
        site = website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')
        self.assertEqual(site.get_id(), 18, "Site ID is not correct.")

    def get_siteinfo_general(self):
        """Test retreival of siteinfo/general."""
        site = website.Website(18, 'WikiApiary', '')
        self.assertEqual(
            site.get_siteinfo_general(),
            False,
            "API URL is not set so this should fail.")

        site = website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')
        self.assertEqual(
            site.get_siteinfo_general(),
            True,
            "API URL is set but failed call to get siteinfo/general.")

    # def test_wikiapiary_version(self):
    #     """Pull the version from WikiApiary."""
    #     site = website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')
    #     #site = website.Website(100, 'Wikipedia (en)', 'https://en.wikipedia.org/w/api.php')
    #     self.assertEqual(
    #         site.get_siteinfo_general(),
    #         True,
    #         "Pulled siteinfo from WikiApiary but failed.")
    #     self.assertEqual(
    #         site.retrieve_siteinfo_general()['generator'],
    #         'MediaWiki 1.22.0rc2',
    #         "Returned invalid value for WikiApiary MediaWiki version.")

    def test_parallel_data(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_general()
        website.Website(100, 'Wikipedia (en)', 'https://en.wikipedia.org/w/api.php').record_general()
        website.Website(54, 'Planet Kubb Wiki', 'http://wiki.planetkubb.com/w/api.php').record_general()

    def test_record_general(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_general()

    def test_record_extensions(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_extensions()

    def test_record_extensions(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_skins()

    def test_record_extensions(self):
        website.Website(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php').record_smwinfo()


if __name__ == '__main__':
    unittest.main()
