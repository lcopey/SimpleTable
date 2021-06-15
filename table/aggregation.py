from typing import Union, Any, Callable
from statistics import mean, stdev
from functools import partial
from .mapped_sequence import MappedSequence


def _aggregate(agg_func: Callable, x: Union[MappedSequence, Any]):
    if len(x) > 1:
        keys = x.where(lambda x: x is not None)
        x = x[keys]
        return agg_func(x)
    else:
        return x


mean_aggregate = partial(_aggregate, mean)
std_aggregate = partial(_aggregate, stdev)
