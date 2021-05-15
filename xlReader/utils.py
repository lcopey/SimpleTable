import functools
import collections
import six


def is_iterable(arg):
    return (
            isinstance(arg, collections.Iterable)
            and not isinstance(arg, six.string_types)
    )


class NullOrder(object):
    """
    Dummy object used for sorting in place of None.

    Sorts as "greater than everything but other nulls."
    """

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        if other is None:
            return False

        return True


def memoize(func):
    """Memoize decorator for instance methods that take no arguments."""""

    @functools.wraps(func)
    def inner(self):
        """Return memoized values"""
        if inner.memo is None:
            inner.memo = func(self)
        return inner.memo

    inner.memo = None
    return inner
