"""
Test extension weekly task.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.bot.extension_weekly import ExtensionWeekly


class TestExtensionWeekly(unittest.TestCase):
    """Run some tests."""

    def test_extension_weekly(self):
        """Run the extensions for now."""

        task = ExtensionWeekly()
        site_count = task.run()
        assert site_count > 0

if __name__ == '__main__':
    unittest.main()
