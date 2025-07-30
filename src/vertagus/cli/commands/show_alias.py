import sys

import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus.cli import utils as cli_utils
from vertagus.aliases import loader as alias_loader


@click.command("show-alias")
@click.argument("alias_name", required=True)
@click.option("--config", "-c", default=None, help="Path to the configuration file")
def show_alias_cmd(alias_name, config):
    master_config = cli_utils.load_config(config, suppress_logging=True)
    project = factory.create_project(cfgtypes.ProjectData.from_project_config(master_config["project"]))
    version = project.get_version()
    if not version:
        click.echo("No version found for the project.")
        sys.exit(1)
    alias_classes = alias_loader.get_aliases([alias_name])
    if not alias_classes:
        click.echo(f"Alias '{alias_name}' not found.")
        sys.exit(1)
    alias_obj = alias_classes[0](version)
    alias = alias_obj.as_string()
    click.echo(alias)
