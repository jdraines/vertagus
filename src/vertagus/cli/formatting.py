import typing as t
from click.formatting import (
    HelpFormatter,
    measure_table,
    iter_rows,
    wrap_text as click_wrap_text
)
from click import style


def wrap_text(text: str,
              width: int,
              initial_indent: str = "",
              subsequent_indent: str = "",
              preserve_paragraphs: bool = False
              ) -> str:
    text = click_wrap_text(
        text,
        width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        preserve_paragraphs=preserve_paragraphs
    )
    lines = []
    for line in text.splitlines():
        if len(line) < width:
            line = line.ljust(width)
        lines.append(line)
    return "\n".join(lines)


def set_col_widths(col_widths: list[int], width: int):
    total_width = sum(col_widths)
    if total_width > width:
        col_widths = [int(width * col_width / total_width) for col_width in col_widths]
    return col_widths


class DisplayTableFormatter(HelpFormatter):
    
    def write_table(self, 
                    rows: t.Sequence[t.Tuple],
                    col_widths: t.Sequence[int],
                    col_spacing: int = 2,
                    header: bool = False
                    ) -> None:
        rows = list(rows)
        col_widths = set_col_widths(col_widths, self.width)
        for row_idx, cells in enumerate(iter_rows(rows, len(rows[0]))):
            is_header = header and row_idx == 0
            row_height = 1
            for idx, cell in enumerate(cells):
                if idx == 0:
                    cell_text = wrap_text(
                        cell,
                        col_widths[idx],
                        " " * self.current_indent,
                        subsequent_indent=" " * self.current_indent
                    )
                else:
                    indent_len = 0
                    for prev_cell_idx in range(0, idx):
                        indent_len += col_widths[prev_cell_idx] + col_spacing
                    cell_text = wrap_text(
                        cell,
                        col_widths[idx],
                        " " * col_spacing,
                        subsequent_indent=" " * indent_len
                    )
                cell_height = cell_text.count("\n") + 1
                row_height = max(row_height, cell_height)
                if cell_height < row_height:
                    cell_text += "\n" * (row_height - cell_height)
                if is_header:
                    cell_text = style(cell_text, bold=True)
                self.write(cell_text)
            self.write("\n")
        self.write("\n")
