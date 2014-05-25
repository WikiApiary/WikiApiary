"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.website.extensions import RecordExtensionsTask


class TestRecordExtensionsTask(unittest.TestCase):
    """Run some tests."""

    def test_record_extensions(self):
        """This should succeed, getting extensions from WikiApiary."""
        task = RecordExtensionsTask()
        retval = task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')
        if 'edit' not in retval:
            raise Exception(retval)

    def test_record_extensions_fake(self):
        """This should fail, the hostname isn't real."""
        task = RecordExtensionsTask()
        with self.assertRaises(Exception):
            task.run(666, 'Fake site', 'http://foo.bar.com/')

if __name__ == '__main__':
    unittest.main()
