
"""
TODO: add description
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.bot.deletewebsitelogs import DeleteWebsiteLogsTask


class TestDeleteWebsiteLogsTask(unittest.TestCase):
    """Execute DeleteBotLogsTask."""

    def test_delete_website_logs(self):
        """Process segment 0."""
        task = DeleteWebsiteLogsTask()
        assert task.run() >= 0

if __name__ == '__main__':
    unittest.main()
