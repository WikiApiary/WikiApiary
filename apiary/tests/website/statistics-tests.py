"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.website.statistics import GetStatisticsTask


class TestGetStatisticsTask(unittest.TestCase):
    """Run some tests."""

    def test_statistics_task(self):
        task = GetStatisticsTask()
        task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')

    def test_statistics_task_fake(self):
        task = GetStatisticsTask()
        assert task.run(666, 'Fake site', 'http://foo.bar.com/') == False
        
if __name__ == '__main__':
    unittest.main()
