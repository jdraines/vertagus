import sys

import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus.cli import utils as cli_utils
from vertagus.cli.options import configless_options


@click.command("show-version")
@click.option("--config", "-c", default=None, help="Path to the configuration file")
@configless_options
def show_version_cmd(config, **cli_opts):
    master_config = cli_utils.resolve_config(config, cli_opts, suppress_logging=True)
    project = factory.create_project(cfgtypes.ProjectData.from_project_config(master_config["project"]))
    version = project.get_version()
    if not version:
        click.echo("No version found for the project.")
        sys.exit(1)
    click.echo(version)
