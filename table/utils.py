from collections.abc import Iterable
import six


def is_iterable(arg):
    return (
            isinstance(arg, Iterable)
            and not isinstance(arg, six.string_types)
    )


def is_scalar(arg):
    return not is_iterable(arg)


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
