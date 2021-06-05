from functools import partial
from typing import Optional, Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .mapped_table import MappedTable


class HtmlFormatter:
    def __init__(self):
        self.float_format = '{:.5f}'
        self.default_format = '{}'
        self.html_table_format = \
            '<div><table>\
                <thead>\
                        {}\
                </thead>\
                <tbody>\
                        {}\
                </tbody>\
            </table></div>'

    def write_cell(self, value: Any, kind: str, tags: Optional[str] = None, cell_format: Optional[str] = None):
        if tags is not None:
            start_tag = f'<{kind} {tags}>'
        else:
            start_tag = f'<{kind}>'

        if isinstance(value, float):
            cell_value = self.float_format.format(value)
        else:
            cell_value = self.default_format.format(value)
        if cell_format is not None:
            cell_value = f'<{cell_format}>{cell_value}</{cell_format}>'

        return f"{start_tag}{cell_value}</{kind}>"

    def format_sequence(self, row, kind: str, cell_format: Optional[str] = None) -> str:
        formatter = lambda x: self.write_cell(value=x, kind=kind, cell_format=cell_format)
        formatted = '\n'.join(map(formatter, row))
        return formatted

    def format_row(self, row, index):
        return self.format_sequence((f'<b>{index}</b>', *row), kind='td')

    def format_header(self, header):
        return self.format_sequence(('', *header), kind='td', cell_format='b')

    def format_table(self, table: 'MappedTable'):
        header = self.format_header(table.columns)

        if len(table) > 11:
            rows = [self.format_row(row, index) for row, index in zip(table.row_values[:5], table.index[:5])]
            inter = self.format_sequence(('...',) * (len(table.columns) + 1), kind='td')
            rows += [inter]
            rows += [self.format_row(row, index) for row, index in zip(table.row_values[-5:], table.index[-5:])]
        else:
            rows = [self.format_row(row, index) for index, row in zip(table.index, table.row_values)]

        rows = self.format_sequence(rows, kind='tr')
        return self.html_table_format.format(header, rows)
