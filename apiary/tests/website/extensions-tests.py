"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.website.extensions import RecordExtentionsTask


class TestRecordExtentionsTask(unittest.TestCase):
    """Run some tests."""

    def test_record_extensions_wikiapiary(self):
        """This should succeed, getting extensions from WikiApiary."""
        task = RecordExtentionsTask()
        assert task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php') == True

    def test_record_extensions_fake(self):
        """This should fail, the hostname isn't real."""
        task = RecordExtentionsTask()
        assert task.run(666, 'Fake site', 'http://foo.bar.com/') == False

if __name__ == '__main__':
    unittest.main()
