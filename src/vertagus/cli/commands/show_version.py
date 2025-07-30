import sys

import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus.cli import utils as cli_utils


@click.command("show-version")
@click.option("--config", "-c", default=None, help="Path to the configuration file")
def show_version_cmd(config):
    master_config = cli_utils.load_config(config, suppress_logging=True)
    project = factory.create_project(cfgtypes.ProjectData.from_project_config(master_config["project"]))
    version = project.get_version()
    if not version:
        click.echo("No version found for the project.")
        sys.exit(1)
    click.echo(version)
