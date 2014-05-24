"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.bot.send_weekly_report import SendWeeklyReport


class TestSendWeeklyReport(unittest.TestCase):
    """Run some tests."""

    def test_send_notification(self):
        """Send a test notification to Thingles."""
        test_site = 'WikiApiary'
        task = SendWeeklyReport()
        message_body = task.generate_weekly_report(test_site)
        task.send_notification(
            'Thingles',
            "[Unittest] Weekly Report for %s" % test_site,
            message_body
        )

    def test_get_notify_list(self):
        """Test checks to insure that Thingles is a subscriber of WikiApiary."""
        task = SendWeeklyReport()
        userlist = task.get_notify_list('WikiApiary')
        if 'Thingles' not in userlist:
            raise Exception('Thingles not found as a subscriber for WikiApiary.')

    def test_get_notify_list_nosite(self):
        """Test checks to insure that Thingles is a subscriber of WikiApiary."""
        task = SendWeeklyReport()
        userlist = task.get_notify_list('There is no website named this')
        assert len(userlist) == 0

if __name__ == '__main__':
    unittest.main()
