import unittest
from table import MappedTable, MappedSequence
from table.api import concat


class TestMappedTable(unittest.TestCase):
    def setUp(self) -> None:
        self.table = MappedTable.from_excel('../datas.xlsx')

    def test_vstack(self):
        self.assertEqual(concat(self.table[0:30], self.table[30:], axis=0), self.table, )

    def test_hstack(self):
        new_table = concat(self.table, MappedSequence(range(len(self.table)), name='ID'), axis=1)
        self.assertIsNotNone(new_table)
