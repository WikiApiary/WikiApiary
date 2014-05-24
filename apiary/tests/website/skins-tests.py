"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.website.skins import RecordSkinsTask


class TestRecordSkinsTask(unittest.TestCase):
    """Run some tests."""

    def test_record_skins(self):
        """Get skins from WikiApiary."""
        task = RecordSkinsTask()
        self.assertEqual(
            task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php'),
            True
        )

    def test_record_skins_fake(self):
        """Get skins from fake website."""
        task = RecordSkinsTask()
        with self.assertRaises(Exception):
            task.run(666, 'Fake site', 'http://foo.bar.com/')

        
if __name__ == '__main__':
    unittest.main()
