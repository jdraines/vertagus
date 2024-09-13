import click

from vertagus.providers.scm.registry import list_scm_types
from vertagus.cli.formatting import DisplayTableFormatter


@click.command('list-scms')
def list_scms_cmd():
    scms: list[str] = list_scm_types()
    formatter = DisplayTableFormatter(max_width=240)
    header = ('SCM Type',)
    rows = [header]
    for scm in scms:
        rows.append((scm, ))
    formatter.write_table(
        rows,
        col_widths=[225],
        header=True
    )
    click.echo()
    click.echo(formatter.getvalue())
    click.echo()
