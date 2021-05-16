from typing import Sequence, Optional, Iterable, Union
from .mapped_sequence import MappedSequence
from .mapped_table import MappedTable


def read_excel(file_path, header: Optional[Union[int, Iterable[int]]] = 0,
               sheetname: Optional[str] = None):
    return MappedTable.from_excel(file_path=file_path, header=header, sheetname=sheetname)
