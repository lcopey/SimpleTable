from collections import Sequence, OrderedDict
from typing import Tuple, Any
import functools


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
    __slots__ = ['_values', '_keys', '_name', '_cache']

    def __init__(self, values, keys=None, name=None):
        self._values = tuple(values)
        if keys is not None:
            assert len(values) == len(keys), 'values and keys should have the same length, got {} and {}'.format(
                len(values), len(keys))
            self._keys = tuple(keys)
        else:
            self._keys = None

        self._name = name
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
        sample = u', '.join(repr(d) for d in self.values()[:5])

        if len(self) > 5:
            sample += u', ...'

        return u'<{}: ({})>'.format(self._name, sample)

    def __str__(self):
        """
        Print an ascii sample of the contents of this sequence.
        """

        return str(self.__unicode__())

    def __repr__(self):
        return self.__str__()

    def _get_from_indices(self, indices):
        values = self.values()
        keys = self.keys()

        new_keys = []
        new_values = []
        for i in indices:
            new_keys.append(keys[i])
            new_values.append(values[i])

        return MappedSequence(new_values, new_keys, name=self._name)

    def __getitem__(self, item):
        """
        Retrieve values from this array by index, slice or key.
        """
        if isinstance(item, slice):
            indices = range(*item.indices(len(self)))
            return self._get_from_indices(indices)

        elif type(item) is list:
            if not all([k in self.keys() for k in item]):
                raise KeyError
            keys = self.keys()
            indices = [keys.index(k) for k in item]
            return self._get_from_indices(indices)


        # Note: can't use isinstance because bool is a subclass of int
        elif type(item) is int:
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

    @memoize
    def items(self) -> Tuple[Tuple[Any, Any]]:
        """
        Equivalent to :meth:`collections.OrderedDict.items`.
        """
        return tuple(zip(self.keys(), self.values()))

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
    def unique(self):
        return tuple(set(self._values))
