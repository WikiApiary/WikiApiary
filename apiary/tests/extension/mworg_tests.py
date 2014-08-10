"""
Test Mediawiki task
"""
# pylint: disable=C0301,W0622

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "apiary.tests"
from apiary.tasks.extension.mw_org import MediawikiTasks


class TestMediawikiTasks(unittest.TestCase):
    """Run some tests."""

    def test_get_mwpagetitle(self):
    	"""Extension:ConfirmEdit returns Extension:ConfirmEdit"""

    	task = MediawikiTasks()
    	assert task.get_mwpagetitle("Extension:ConfirmEdit") == "Extension:ConfirmEdit"
    	assert task.get_mwpagetitle("Extension:Confirm User Accounts") == "Extension:ConfirmAccount"

    def test_get_rating(self):
    	"""Extension:ConfirmEdit has ratings on it"""

    	task = MediawikiTasks()
    	assert task.get_mwpagetitle("Extension:ConfirmEdit") > 0

    def test_mediawiki_tasks(self):
    	"""Run the extensions for now."""

    	task = MediawikiTasks()
    	task.run("Extension:ConfirmEdit")


if __name__ == '__main__':
    unittest.main()