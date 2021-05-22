import unittest
from table import MappedSequence


class TestMappedSequenceUse(unittest.TestCase):
    def setUp(self) -> None:
        self.mapped_sequence = MappedSequence([0, 1, 2], ['a', 'b', 'c'], 'name')

    def test_values(self):
        self.assertEqual(self.mapped_sequence.values(), (0, 1, 2))

    def test_keys(self):
        self.assertEqual(self.mapped_sequence.keys(), ('a', 'b', 'c'))

    def test_items(self):
        self.assertEqual(self.mapped_sequence.items(), (('a', 0), ('b', 1), ('c', 2)))

    def test_get_item(self):
        self.assertEqual(self.mapped_sequence[0], 0)
        self.assertEqual(self.mapped_sequence[1], 1)
        self.assertEqual(self.mapped_sequence[2], 2)
        self.assertEqual(self.mapped_sequence[:], (0, 1, 2))
        self.assertEqual(self.mapped_sequence[0::2], (0, 2))
        self.assertEqual(self.mapped_sequence['a'], 0)
        self.assertEqual(self.mapped_sequence['b'], 1)
        self.assertEqual(self.mapped_sequence['c'], 2)

    def test_unique(self):
        self.assertEqual(self.mapped_sequence.unique(), (0, 1, 2))

    def test_fillnone(self):
        sequence = self.mapped_sequence.reindex(['a', 'b', 'c', 'd'])
        self.assertEqual(sequence, (0, 1, 2, None))
        self.assertEqual(sequence.fillnone(0), (0, 1, 2, 0))
