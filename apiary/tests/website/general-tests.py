"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.website.general import RecordGeneralTask


class TestRecordGeneralTask(unittest.TestCase):
    """Run some tests."""

    def test_record_general(self):
        task = RecordGeneralTask()
        task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')

if __name__ == '__main__':
    unittest.main()
