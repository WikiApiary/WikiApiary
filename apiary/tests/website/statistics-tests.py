"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.website.statistics import GetStatisticsTask


class TestGetStatisticsTask(unittest.TestCase):
    """Test the GetStatisticsTask methods."""

    def test_statistics_task(self):
        """Ask for statistics via API"""
        task = GetStatisticsTask()
        self.assertEqual(
            task.run(18, 'WikiApiary', 'API', 'https://wikiapiary.com/w/api.php', None),
            True
        )

    def test_statistics_stats_task(self):
        """Asking for statistics via the Stats URL"""
        task = GetStatisticsTask()
        self.assertEqual(
            task.run(10898, '311wiki', 'Statistics', None, 'http://www.taiyedbrodels.com/wiki/index.php?title=Special:Statistics'),
            True
        )

    def test_statistics_task_fake(self):
        """Calling a fake website."""
        task = GetStatisticsTask()
        with self.assertRaises(Exception):
            task.run(666, 'Fake site', 'API', 'http://foo.bar.com/', None)
        
if __name__ == '__main__':
    unittest.main()
