"""
Exercise the Website class to insure the methods operate
as expected.
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from WikiApiary.apiary.tasks.bot.websitesegment import ProcessWebsiteSegment


class TestProcessWebsiteSegment(unittest.TestCase):
    """Run some tests."""

    # def test_segment_zero(self):
    #     """Process segment 0."""
    #     task = ProcessWebsiteSegment()
    #     task.run(0)

if __name__ == '__main__':
    unittest.main()
