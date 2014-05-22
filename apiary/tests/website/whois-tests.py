"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.website.whoislookup import RecordWhoisTask


class TestRecordWhoisTask(unittest.TestCase):
    """Run some tests."""

    def test_whois_task(self):
        """Get whois information from WikiApiary."""
        task = RecordWhoisTask()
        self.assertEqual(
            task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php'),
            True
        )

    def test_whois_task_fake(self):
        """Get whois information from fake website."""
        task = RecordWhoisTask()
        with self.assertRaises(Exception):
            task.run(666, 'Fake site', 'http://foo.bar.com/')
        
if __name__ == '__main__':
    unittest.main()
