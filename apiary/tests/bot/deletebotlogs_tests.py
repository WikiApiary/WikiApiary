
"""
TODO: add description
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.bot.deletebotlogs import DeleteBotLogsTask


class TestDeleteBotLogsTask(unittest.TestCase):
    """Execute DeleteBotLogsTask."""

    def test_delete_bot_logs(self):
        """Process segment 0."""
        task = DeleteBotLogsTask()
        assert task.run() >= 0

if __name__ == '__main__':
    unittest.main()
