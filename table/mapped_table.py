from typing import Iterable, Optional, Union, List, Sequence
from functools import partial
from openpyxl import load_workbook
from .mapped_sequence import MappedSequence
from .utils import is_iterable


class MappedTable:
    """A generic container for immutable 2-dimensional data"""
    __slots__ = ['_values', '_index', '_columns']

    def __init__(self, values: Sequence[Sequence], columns: Sequence[str], index: Optional[Iterable] = None,
                 axis=0):
        """

        Parameters
        ----------
        values: Iterable[Iterable]
            Typically 2D-nested list of rows
        columns: Iterable
            List of the names of the columns
        index : Optional[Iterable]
            List of the names of the rows
        axis: int
            Orientation of the values. If axis = 0, values are Iterable of rows. If axis = 1, values are Iterable of
            columns.
        """

        if axis == 0:
            if index is None:
                index = range(len(values))
            values = list(zip(*values))
        else:
            if index is None:
                index = range(len(values[0]))

        # index and columns are also used as keys to ease slicing.
        self._index = MappedSequence(index, index)
        self._columns = MappedSequence(columns, columns)

        # Store as MappedSequence of columns
        values_as_columns = [MappedSequence(values=value, keys=index, name=col) for value, col in zip(values, columns)]
        self._values = MappedSequence(values=values_as_columns, keys=columns)

        # Store as MappedSequence of rows
        # self._values = MappedSequence([MappedSequence(value, columns, idx) for value, idx in zip(values, index)], index)

    @classmethod
    def from_excel(cls, file_path, header: Optional[Union[int, Iterable[int]]] = 0,
                   sheetname: Optional[str] = None):
        """

        Parameters
        ----------
        file_path: path to excel file
        header: Optional[Union[int, Iterable[int]]]
            If header is None, the columns are defined as a sequence of integers.
        sheetname: Optional[str]
            Name of the sheet to parse. If None, the first will used instead.

        Returns
        -------

        """
        # Get workbook
        workbook = load_workbook(file_path, data_only=True)
        # Handle sheetname
        # By default, parse the first sheet in the excel
        if sheetname is None:
            sheetname = workbook.sheetnames[0]
        sheet = workbook[sheetname]

        # Handle header
        # 1. Instantiate columns
        # 2. Instantiate values as list of rows
        if header is None:
            values = [row for n, row in enumerate(sheet.iter_rows(values_only=True))]
            columns = range(len(values[0]))

        elif is_iterable(header):
            columns = list(
                zip(*[row for row in sheet.iter_rows(min_row=min(header), max_row=max(header) + 1, values_only=True)])
            )
            values = [row for n, row in enumerate(sheet.iter_rows(values_only=True)) if n not in header]

        elif type(header) == int:
            columns = [row for row in sheet.iter_rows(min_row=header, max_row=header + 1, values_only=True)][0]
            values = [row for n, row in enumerate(sheet.iter_rows(values_only=True)) if n != header]

        else:
            raise ValueError

        return cls(values=values, columns=columns, axis=0)

    @property
    def index(self):
        return self._index

    @property
    def columns(self):
        return self._columns

    @property
    def values(self) -> 'MappedSequence':
        return self._values

    def __str__(self):
        """
        Print an ascii sample of the contents of this sequence.
        """

        return self.values.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        # In case key is not iterable, slice the columns
        if not is_iterable(key) and type(key) is not slice and type(key) is not list:
            values = self.values[key]
            # return MappedTable(values=[values], columns=[values.name], index=self.index, axis=1)
            return values

        elif type(key) is list:
            values = self.values[key]
            return MappedTable(values=values, columns=values.keys(), index=self.index, axis=1)

        elif type(key) is slice:
            new_index = self.index[key]
            new_values = [value[key] for value in self.values]
            return MappedTable(values=new_values, index=new_index, columns=self.columns, axis=1)

        elif type(key) is tuple and len(key) == 2:
            # start by slicing the columns
            new_columns = self.columns[key[1]]
            new_index = self.index[key[0]]
            subset = self.values[key[1]]
            # check if the subset is 2dimensional or 1d
            if isinstance(subset[0], MappedSequence):
                new_values = [value[key[0]] for value in subset]
            else:
                new_values = [subset[key[0]]]
                new_columns = [new_columns]

            return MappedTable(values=new_values, index=new_index, columns=new_columns, axis=1)

    def __len__(self):
        return len(self.index)

    def __eq__(self, other: 'MappedTable') -> bool:
        result = self.columns == other.columns
        result &= self.values == other.values
        return result

    @property
    def shape(self):
        return len(self.index), len(self.columns)

    def sort_values(self, key: Union[int, str, Iterable[str]], ascending: bool = True) -> 'MappedTable':
        """

        Parameters
        ----------
        key: Union[int, str, Iterable[str]]
            key used to sort the table. It can be an integer (position of the column) or the name of the column
            passed as a string or a list of string.
        ascending : bool
            sort values in ascending ordre if True

        Returns
        -------
        MappedTable
        Sorted table
        """
        values_as_rows = self.to_list()
        sort_key = partial(MappedSequence.__getitem__, item=key)
        sorted_values = sorted(values_as_rows, key=sort_key, reverse=not ascending)
        new_index = tuple(value.name for value in sorted_values)
        return MappedTable(values=sorted_values, index=new_index, columns=self.columns)

    def _get_empty_sequence(self, ):
        return (None,) * self.shape[0]

    def reindex(self, columns):
        values = [self.values.get(value, self._get_empty_sequence()) for value in columns]
        return MappedTable(values=values, index=self.index, columns=columns, axis=1)

    def to_list(self):
        return [MappedSequence(row, self.columns, name=name) for name, *row in zip(self.index, *self.values)]
