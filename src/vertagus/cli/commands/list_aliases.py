import click

from vertagus.core.tag_base import AliasBase
from vertagus.aliases.loader import load_aliases
from vertagus.cli.formatting import DisplayTableFormatter


@click.command('list-aliases')
def list_aliases_cmd():
    aliases: list[type[AliasBase]] = sorted(load_aliases(), key=lambda x: x.name)
    formatter = DisplayTableFormatter(max_width=240)
    header = ('Alias Name', 'Description')
    rows = [header]
    for alias in aliases:
        rows.append((alias.name, alias.description))
    formatter.write_table(
        rows,
        col_widths=[30, 120],
        header=True
    )
    click.echo()
    click.echo(formatter.getvalue())
    click.echo()
