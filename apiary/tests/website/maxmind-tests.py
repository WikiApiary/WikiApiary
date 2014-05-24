"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622,R0201,R0904

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.website.maxmind import MaxmindTask


class TestMaxmindTask(unittest.TestCase):
    """Run some tests."""

    def test_maxmind_task(self):
        """Get MaxMind data for WikiApiary."""
        task = MaxmindTask()
        self.assertEqual(
            task.run(18, 'WikiApiary', 'https://wikiapiary.com/w/api.php'),
            True
        )

    def test_maxmind_task_fake(self):
        """Get MaxMind from fake website."""
        task = MaxmindTask()
        with self.assertRaises(Exception):
            task.run(666, 'Fake site', 'http://foo.bar.com/')


if __name__ == '__main__':
    unittest.main()
