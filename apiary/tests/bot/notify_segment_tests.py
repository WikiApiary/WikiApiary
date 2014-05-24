"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.bot.notify_segment import NotifySegment


class TestNotifySegment(unittest.TestCase):
    """Run some tests."""

    def get_websites_to_notify(self):
        """This gets websites from the segment that WikiApiary is in."""

        curr_day = 4
        curr_hour = 18

        task = NotifySegment()
        sites = task.get_notify_sites(curr_day, curr_hour)
        if 'WikiApiary' not in sites:
            raise Exception('WikiApiary not in list of sites returned.')

if __name__ == '__main__':
    unittest.main()
