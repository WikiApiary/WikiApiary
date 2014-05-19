"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.website.maxmind import MaxmindTask


class TestMaxmindTask(unittest.TestCase):
    """Run some tests."""

    def test_maxmind_task(self):
        """Get MaxMind data for WikiApiary."""
        task = MaxmindTask()
        task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php')

    def test_maxmind_task_fake(self):
        """Get MaxMind from fake website."""
        task = MaxmindTask()
        assert task.run(666, 'Fake site', 'http://foo.bar.com/') == False

if __name__ == '__main__':
    unittest.main()
