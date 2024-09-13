import click

from vertagus.core.manifest_base import ManifestBase
from vertagus.providers.manifest.registry import list_manifest_types
from vertagus.cli.formatting import DisplayTableFormatter


@click.command('list-manifests')
def list_manifests_cmd():
    manifests: list[type[ManifestBase]] = list_manifest_types()
    formatter = DisplayTableFormatter(max_width=240)
    header = ('Manifest Type', 'Description')
    rows = [header]
    for manifest in manifests:
        rows.append((manifest.manifest_type, manifest.description))
    formatter.write_table(
        rows,
        col_widths=[30, 120],
        header=True
    )
    click.echo()
    click.echo(formatter.getvalue())
    click.echo()
