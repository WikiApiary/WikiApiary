"""
Run tests on farm class.
"""

import unittest
if __name__ == "__main__" and __package__ is None:
    __package__ = "WikiApiary.apiary.tests"
from apiary import farm


class test_farm(unittest.TestCase):
    """Run some tests."""

    def setUp(self):
        pass

    def test_farm_id(self):
        """ Test farm ID method"""
        my_farm = farm.Farm(25)
        self.assertEqual(my_farm.get_id(), 25, "Farm ID is not correct.")


if __name__ == '__main__':
    unittest.main()
