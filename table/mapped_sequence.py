from collections import Sequence, OrderedDict
from typing import Union, Tuple, Any
import types
import functools
from .utils import is_scalar


def memoize(func):
    """Memoize decorator for instance methods that take no arguments."""""

    @functools.wraps(func)
    def inner(self):
        """Return memoized values"""

        if self._cache.get(func.__name__) is None:
            self._cache[func.__name__] = func(self)
            # print(inner.memo)
        return self._cache.get(func.__name__)

    return inner


class MappedSequence(Sequence):
    """
    A generic container for immutable data that can be accessed either by
    numeric index or by key. This is similar to an
    :class:`collections.OrderedDict` except that the keys are optional and
    iteration over it returns the values instead of keys.

    This is the base class for both :class:`.Column` and :class:`.Row`.

    :param values:
        A sequence of values.
    :param keys:
        A sequence of keys.
    """
    __slots__ = ['_values', '_keys', '_name', '_cache', '_scalar']

    def __init__(self, values, keys=None, name=None):
        self._values = tuple(values)
        if all([is_scalar(value) for value in self._values]):
            self._scalar = True
        else:
            self._scalar = False

        if keys is not None:
            assert len(values) == len(keys), 'values and keys should have the same length, got {} and {}'.format(
                len(values), len(keys))
            self._keys = tuple(keys)
        else:
            self._keys = tuple(range(len(values)))

        self._name = name
        # cache to speed execution of some methods
        # function results are cached using the function name as key
        self._cache = dict()

    def __getstate__(self):
        """
        Return state values to be pickled.

        This is necessary on Python2.7 when using :code:`__slots__`.
        """
        return {
            '_values': self._values,
            '_keys': self._keys,
            '_name': self._name
        }

    def __setstate__(self, data):
        """
        Restore pickled state.

        This is necessary on Python2.7 when using :code:`__slots__`.
        """
        self._values = data['_values']
        self._keys = data['_keys']
        self._name = data['_name']

    def __unicode__(self):
        """
        Print a unicode sample of the contents of this sequence.
        """
        if len(self) <= 10:
            sample = ', '.join(repr(d) for d in self.values())
        else:
            sample = u', '.join(repr(d) for d in self.values()[:3])
            sample += ', ...,' + ', '.join(repr(d) for d in self.values()[-3:])

        return u'{}: ({})'.format(self._name, sample)

    def __str__(self):
        """
        Print an ascii sample of the contents of this sequence.
        """

        return str(self.__unicode__())

    def __repr__(self):
        if len(self) > 11:
            rows = [f"{index}\t{value}" for value, index in zip(self.values()[:5], self.keys()[:5])]
            rows += ['...\t...']
            rows += [f"{index}\t{value}" for value, index in zip(self.values()[-5:], self.keys()[-5:])]
        else:
            rows = [f"{index}\t{value}" for value, index in zip(self.values(), self.keys())]
        rows = '\n'.join(rows)
        footer = f'Name: {self.name}, Length: {self.__len__()}'
        return rows + '\n' + footer

    def _get_sequence_from_indices(self, indices):
        values = self.values()
        keys = self.keys()

        # if the list has only one item, it should return a sequence anyway
        if len(indices) == 1:
            new_values = [values[indices[0]]]
            new_keys = [keys[indices[0]]]
        # else return MappedSequence
        else:
            new_keys = []
            new_values = []
            for i in indices:
                new_keys.append(keys[i])
                new_values.append(values[i])

        return MappedSequence(new_values, new_keys, name=self._name)

    def __getitem__(self, item) -> Union['MappedSequence', Any]:
        """
        Retrieve values from this array by index, list of index, slice or key.
        """
        if isinstance(item, slice):
            indices = range(*item.indices(len(self)))
            return self._get_sequence_from_indices(indices)

        elif type(item) is list or isinstance(item, MappedSequence):

            item_in_keys = [k in self.keys() for k in item]
            # in the case the list contains numerical index that does not match the keys
            if all([type(k) is int and k not in self.keys() for k in item]):
                return self._get_sequence_from_indices(item)
            # in the case the list contains directly the keys of the sequence
            elif all(item_in_keys):
                keys = self.keys()
                indices = [keys.index(k) for k in item]
                return self._get_sequence_from_indices(indices)
            else:
                raise KeyError

        # Note: can't use isinstance because bool is a subclass of int
        elif type(item) is int and item not in self.keys():
            return self.values()[item]
        else:
            return self.dict()[item]

    def __setitem__(self, key, value):
        """
        Set values by index, which we want to fail loudly.
        """
        raise TypeError('Rows and columns can not be modified directly. You probably need to compute a new column.')

    def __iter__(self):
        """
        Iterate over values.
        """
        return iter(self.values())

    @memoize
    def __len__(self):
        return len(self.values())

    def __eq__(self, other):
        """
        Equality tests with other sequences.
        """
        if not isinstance(other, Sequence):
            return False

        return self.values() == tuple(other)

    def __ne__(self, other):
        """
        Inequality tests with other sequences.
        """
        return not self.__eq__(other)

    def __lt__(self, other: 'MappedSequence'):
        """
        Lower than test with other sequences
        """
        return self._values < other.values()

    def __gt__(self, other: 'MappedSequence'):
        """
        Greater than test with other sequences
        """
        return self._values > other.values()

    def __contains__(self, value):
        return self.values().__contains__(value)

    def keys(self) -> tuple:
        """
        Equivalent to :meth:`collections.OrderedDict.keys`.
        """
        return self._keys

    def values(self) -> tuple:
        """
        Equivalent to :meth:`collections.OrderedDict.values`.
        """
        return self._values

    def __hash__(self):
        """Hashed value correspond"""
        return hash(self._values)

    @memoize
    def items(self) -> Tuple[Tuple[Any, Any]]:
        """
        Equivalent to :meth:`collections.OrderedDict.items`.
        """
        return tuple(zip(self.keys(), self.values()))

    @property
    def name(self):
        return self._name

    def get(self, key, default=None):
        """
        Equivalent to :meth:`collections.OrderedDict.get`.
        """
        try:
            return self.dict()[key]
        except KeyError:
            if default:
                return default
            else:
                return None

    @memoize
    def dict(self):
        """
        Retrieve the contents of this sequence as an
        :class:`collections.OrderedDict`.
        """
        if self.keys() is None:
            raise KeyError

        return OrderedDict(self.items())

    @memoize
    def unique(self) -> tuple:
        """Retrieve unique set of values in the mapped_sequence"""
        return tuple(set(self._values))

    def reindex(self, index):
        """Reindex

        Parameters
        ----------
        index

        Returns
        -------

        """
        if self._scalar:
            return MappedSequence(
                values=tuple(self.get(value, None) for value in index),
                keys=index, name=self.name
            )
        else:
            raise KeyError

    def to_list(self):
        return list(self.values())

    def isnone(self):
        new_values = [value is None for value in self.values()]
        return MappedSequence(values=new_values, keys=self.keys(), name=self.name)

    def fillnone(self, value):
        return MappedSequence([value if item is None else item for item in self.values()],
                              keys=self.keys(), name=self.name)

    def where(self, target_or_func):
        def compare(x):
            return x == target_or_func

        if isinstance(target_or_func, types.FunctionType):
            check = target_or_func
        else:
            check = compare

        new_keys = []
        new_values = []
        for key, value in zip(self._keys, self._values):
            if check(value):
                new_keys.append(key)
                new_values.append(value)

        return new_keys
