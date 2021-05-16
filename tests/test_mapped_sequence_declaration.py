import unittest
from table import MappedSequence


class TestMappedSequence(unittest.TestCase):
    def test_init(self):
        self.assertIsNotNone(MappedSequence(values=(0, 1, 2), keys=['a', 'b', 'c']))
        self.assertIsNotNone(MappedSequence(values=(0, 1, 2)))
        self.assertRaises(AssertionError, MappedSequence, values=(0, 1, 2), keys=['a', 'b'])
