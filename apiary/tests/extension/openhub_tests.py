"""
Test OpenHub task
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.extension.openhub import OpenHubTask


class TestOpenHubTask(unittest.TestCase):
    """Run some tests."""

    def test_get_openhub_name(self):
        """Extension:Validator returns Validator"""
        task = OpenHubTask()
        assert task.get_openhub_name('Extension:Validator') == "validator"

    def test_openhub_task(self):
        """Run the extensions for now."""

        task = OpenHubTask()
        task.run('Extension:Validator')


if __name__ == '__main__':
    unittest.main()
