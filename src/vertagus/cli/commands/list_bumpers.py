import click

from vertagus.bumpers.registry import list_bumpers
from vertagus.cli.formatting import DisplayTableFormatter


@click.command('list-bumpers')
def list_bumpers_cmd():
    bumpers: list[str] = list_bumpers()
    formatter = DisplayTableFormatter(max_width=240)
    header = ('Version Bumpers',)
    rows = [header]
    for bumper in bumpers:
        rows.append((bumper, ))
    formatter.write_table(
        rows,
        col_widths=[225],
        header=True
    )
    click.echo()
    click.echo(formatter.getvalue())
    click.echo()
