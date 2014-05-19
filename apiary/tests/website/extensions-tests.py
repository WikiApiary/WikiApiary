"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.website.extensions import RecordExtensionsTask


class TestRecordExtensionsTask(unittest.TestCase):
    """Run some tests."""

    def test_record_extensions(self):
        """This should succeed, getting extensions from WikiApiary."""
        task = RecordExtensionsTask()
        assert task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php') == True

    def test_record_extensions_fake(self):
        """This should fail, the hostname isn't real."""
        task = RecordExtensionsTask()
        assert task.run(666, 'Fake site', 'http://foo.bar.com/') == False

if __name__ == '__main__':
    unittest.main()
