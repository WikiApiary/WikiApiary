"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.website.general import RecordGeneralTask


class TestRecordGeneralTask(unittest.TestCase):
    """Test the methods that access general siteinfo."""

    def test_record_general(self):
        """Get general site information from WikiApiary."""
        task = RecordGeneralTask()
        self.assertEqual(
            task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php'),
            True
        )

    def test_record_general_fake(self):
        """Get general site information from non-existent website."""
        task = RecordGeneralTask()
        with self.assertRaises(Exception):
            task.run(18, 'Foo', 'https://foo.bar.com')


if __name__ == '__main__':
    unittest.main()
