# from collections import OrderedDict
from typing import Sequence, Optional, Iterable, Union
from .mapped_sequence import MappedSequence
from .mapped_table import MappedTable
from .ordered_set import OrderedSet
from .utils import is_scalar, is_iterable


def read_excel(file_path, header: Optional[Union[int, Iterable[int]]] = 0,
               sheetname: Optional[str] = None, skiprows=None):
    return MappedTable.from_excel(file_path=file_path, header=header, sheetname=sheetname, skiprows=skiprows)


def concat(*args, axis=0):
    if axis == 0:
        return _vstack(*args)
    else:
        return _hstack(*args)


def _hstack(*args):
    """Horizontal stack"""
    index = set()
    values = []
    columns = []

    # get union of all index
    for arg in args:
        if isinstance(arg, MappedTable):
            index = index.union(arg.index)
        elif isinstance(arg, MappedSequence):
            index = index.union(arg.keys())
        else:
            raise ValueError

    # Get all values and column names
    # ignore column duplicates
    for arg in args:
        if isinstance(arg, MappedTable):
            for sequence in arg:
                if sequence.name not in columns:
                    columns.append(sequence.name)
                    values.append(sequence.reindex(index))
        elif isinstance(arg, MappedSequence):
            if arg.name not in columns:
                columns.append(arg.name)
                values.append(arg.reindex(index))

    return MappedTable(values=values, columns=columns, index=index, axis=1)


def _vstack(*args):
    """Vertical stack"""
    values = []
    # use the keys of ordered dict as ordered set
    columns = OrderedSet()

    # Union of all columns
    for arg in args:
        if isinstance(arg, MappedTable):
            columns = columns.union(OrderedSet(arg.columns))
        else:
            raise ValueError

    for arg in args:
        values.extend(arg.reindex(columns).to_list())

    return MappedTable(values=values, columns=columns)


def merge(left: MappedTable, right: MappedTable, on=None, left_on=None, right_on=None, how='inner',
          suffixes=('_x', '_y')):
    assert isinstance(left, MappedTable) and isinstance(right, MappedTable), \
        'left and right should be instance of MappedTable'
    assert on is not None or (left_on is not None and right_on is not None), \
        'either `on` argument or left_on and right_on should not be None'

    how_ = {'left', 'right', 'inner', 'outer'}
    assert how in how_, 'how should be one of {}, got {} instead'.format(how_, how)

    # parse arguments
    if on is not None:
        left_on = on
        right_on = on
    assert is_scalar(left_on) and is_scalar(right_on), 'merge are only supported on one columns'
    assert left_on in left.columns, '{} not found in columns of left'.format(left_on)
    assert right_on in right.columns, '{} not found in columns of right'.format(right_on)

    # set the join condition on the first column
    left_columns = [left_on, *[col for col in left.columns if col != left_on]]
    right_columns = [right_on, *[col for col in right.columns if col != right_on]]

    new_columns = [left_on] if left_on == right_on else [left_on, right_on]
    for col in left_columns[1:]:
        new_columns.append(col if col not in right_columns else col + suffixes[0])
    for col in right_columns[1:]:
        new_columns.append(col if col not in left_columns else col + suffixes[1])

    # First sort the values
    left = left[left_columns].sort_values(key=left_on, ascending=True).to_list()
    right = right[right_columns].sort_values(key=right_on, ascending=True).to_list()
    left_len, right_len = len(left), len(right)
    left_i = right_i = 0

    # Does not count the on columns
    left_column_count = len(left_columns) - 1
    right_column_count = len(right_columns) - 1

    new_values = []
    left_added = False
    right_added = False

    def get_tuple(join_id, left_values, right_values):
        left_ = left_values if is_iterable(left_values) else [left_values]
        right_ = right_values if is_iterable(right_values) else [right_values]
        if len(left_) < left_column_count and len(left_) == 1:
            left_ *= left_column_count

        if len(right_) < right_column_count and len(right_) == 1:
            right_ *= right_column_count

        return (join_id, *left_, *right_)

    while (left_i < left_len) & (right_i < right_len):
        left_id = left[left_i][0]
        right_id = right[right_i][0]
        if left_id < right_id and how in ['left', 'outer'] and not left_added:
            # append the line only on a left join
            new_values.append(get_tuple(left_id, left[left_i][1:], None))
            left_added = False
            left_i += 1

        elif left_id > right_id and how in ['right', 'outer'] and not right_added:
            # append the line only on a right join
            new_values.append(get_tuple(right_id, None, right[right_i][1:]))
            right_added = False
            right_i += 1

        elif left_id == right_id:
            # append the line whatever the join method
            new_values.append(get_tuple(left_id, left[left_i][1:], right[right_i][1:]))
            left_added = True
            right_added = True
            right_i += 1

        else:
            if left_id < right_id:
                left_i += 1
            else:
                right_i += 1

    return MappedTable(values=new_values, columns=new_columns)
