import unittest
from table import MappedTable, MappedSequence, concat, merge


class TestMappedTable1(unittest.TestCase):
    def setUp(self) -> None:
        self.table = MappedTable.from_excel('../iris.xlsx')

    def test_slice(self):
        self.assertIsNotNone(self.table[0])
        # self.assertRaises(KeyError, self.table.__getitem__, [[0]])
        self.assertIsNotNone(self.table[0:1])
        self.assertIsNotNone(self.table[0:10])
        self.assertIsNotNone(self.table[0, 'sepal length (cm)'])
        self.assertIsNotNone(self.table[:, ['sepal length (cm)']])
        self.assertIsNotNone(self.table[['sepal length (cm)']])
        self.assertIsNotNone(self.table[0:1, 'sepal length (cm)'])
        self.assertIsNotNone(self.table[0:10, 'sepal length (cm)'])
        self.assertIsNotNone(self.table[0, ['sepal length (cm)', 'petal length (cm)']])
        self.assertIsNotNone(self.table[0:1, ['sepal length (cm)', 'petal length (cm)']])
        self.assertIsNotNone(self.table[0:10, ['sepal length (cm)', 'petal length (cm)']])
        self.assertIsNotNone(self.table[[0, 2], ['sepal length (cm)', 'petal length (cm)']])
        self.assertIsNotNone(self.table[2, :])
        for sequence in self.table:
            self.assertIsNotNone(sequence)
            self.assertIsInstance(sequence, MappedSequence)

    def test_sort(self):
        self.assertIsNotNone(self.table.sort_values(0))
        self.assertIsNotNone(self.table.sort_values('sepal length (cm)'))
        self.assertIsNotNone(self.table.sort_values(['sepal length (cm)', 'sepal width (cm)']))

    def test_vstack(self):
        self.assertEqual(concat(self.table[0:30], self.table[30:], axis=0), self.table, )

    def test_hstack(self):
        new_table = concat(self.table, MappedSequence(range(len(self.table)), name='ID'), axis=1)
        self.assertIsNotNone(new_table)

    def test_inner_merge(self):
        new_table = concat(self.table, MappedSequence(range(len(self.table)), name='ID'), axis=1)
        left = new_table[['ID', 'sepal length (cm)']]
        right = new_table[['ID', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]
        self.assertIsNotNone(merge(left, right, on='ID', how='inner'))

    def test_left_merge(self):
        new_table = concat(self.table, MappedSequence(range(len(self.table)), name='ID'), axis=1)
        left = new_table[:, ['ID', 'sepal length (cm)']]
        right = new_table[10:, ['ID', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]
        result = merge(left, right, on='ID', how='left')
        self.assertIsInstance(result, MappedTable)
        self.assertEqual(result.shape, (150, 5))

        left = new_table[1:, ['ID', 'sepal length (cm)']]
        right = new_table[:, ['ID', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]

        result = merge(left, right, on='ID', how='left')
        self.assertIsInstance(result, MappedTable)
        self.assertEqual(result.shape, (149, 5))

        result = merge(left, right, on='ID', how='right')
        self.assertIsInstance(result, MappedTable)
        self.assertEqual(result.shape, (150, 5))

        result = merge(left, right, on='ID', how='outer')
        self.assertIsInstance(result, MappedTable)
        self.assertEqual(result.shape, (150, 5))

    def test_fillnone(self):
        new_columns = self.table.columns
        new_columns = ('ID',) + tuple(new_columns)
        result = self.table.reindex(new_columns)
        self.assertEqual(result.shape, (150, 5))
        self.assertEqual(result[0, :], (None, 5.1, 3.5, 1.4, 0.2))

        result = result.fillnone(0)
        self.assertEqual(result.shape, (150, 5))
        self.assertEqual(result[0, :], (0, 5.1, 3.5, 1.4, 0.2))

    def test_melt(self):
        new_table = concat(self.table, MappedSequence(range(len(self.table)), name='ID'), axis=1)
        new_table = new_table.melt('ID')
        self.assertEqual(new_table.columns, ('ID', 'variable', 'value'))
        self.assertEqual(new_table.shape, (len(self.table)*len(self.table.columns), 3))


class TestMappedTable2(unittest.TestCase):
    def setUp(self) -> None:
        self.table = MappedTable.from_excel('../experiment.xlsx')

    def test_get_attr(self):
        self.assertIsInstance(self.table.experiment_1, MappedSequence)
