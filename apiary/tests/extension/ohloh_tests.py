"""
Test Ohloh task
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.extension.ohloh import OhlohTask


class TestOhlohTask(unittest.TestCase):
    """Run some tests."""

    def test_get_ohloh_name(self):
        """Extension:Validator returns Validator"""
        task = OhlohTask()
        assert task.get_ohloh_name('Extension:Validator') == "validator"

    def test_ohloh_task(self):
        """Run the extensions for now."""

        task = OhlohTask()
        task.run('Extension:Validator')


if __name__ == '__main__':
    unittest.main()
