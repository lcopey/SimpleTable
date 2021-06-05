import unittest
from table import MappedTable


class TestMappedTable(unittest.TestCase):
    def test_init(self):
        self.assertIsNotNone(MappedTable([(0, 1, 2), (0, 1, 2)], columns=['a', 'b', 'c']))
        self.assertIsNotNone(MappedTable([(0, 1, 2), (0, 1, 2)], columns=['a', 'b'], axis=1))
        self.assertIsNotNone(MappedTable.from_excel('../iris.xlsx'))
        self.assertIsNotNone(MappedTable.from_excel('../iris.xlsx', skiprows=2))
