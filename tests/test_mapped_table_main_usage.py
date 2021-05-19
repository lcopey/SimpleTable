import unittest
from table import MappedTable, MappedSequence


class TestMappedTable(unittest.TestCase):
    def setUp(self) -> None:
        self.table = MappedTable.from_excel('../datas.xlsx')

    def test_slice(self):
        self.assertIsNotNone(self.table[0:1])
        self.assertIsNotNone(self.table[0:1, 0:1])
        self.assertIsNotNone(self.table[0:1, 'sepal length (cm)'])
        self.assertIsNotNone(self.table[0:1, ['sepal length (cm)', 'petal length (cm)']])
        self.assertIsNotNone(self.table[[0, 2], ['sepal length (cm)', 'petal length (cm)']])
        for sequence in self.table:
            self.assertIsNotNone(sequence)
            self.assertIsInstance(sequence, MappedSequence)

    def test_sort(self):
        self.assertIsNotNone(self.table.sort_values(0))
        self.assertIsNotNone(self.table.sort_values('sepal length (cm)'))
        self.assertIsNotNone(self.table.sort_values(['sepal length (cm)', 'sepal width (cm)']))
