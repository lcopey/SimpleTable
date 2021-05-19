import sqlite3
from typing import Iterable, Sequence, Optional
from .datatypes import get_datatypes


class DataModel:
    def __init__(self):
        self._db = sqlite3.connect('file:cachedb?mode=memory&cache=shared')

    def _execute(self, query: str):
        with self._db:
            cur = self._db.cursor()
            cur.execute(query)

    def create_table(self, name, columns: Sequence[str], dtypes: Optional[Sequence[type]] = None):
        assert len(columns) == len(dtypes)
        # TODO sanitize column and keep the corresponding values in labels attributes
        query = 'CREATE TABLE IF NOT EXISTS {}({})'
        if dtypes is None:
            col_query = ', '.join(columns)
        else:
            col_query = ', '.join([col + ' ' + get_datatypes(dtype) for col, dtype in zip(columns, dtypes)])
        query = query.format(name, col_query)
        self._execute(query)
