import sys

import click

from vertagus import factory
from vertagus.aliases import loader as alias_loader
from vertagus.cli import utils as cli_utils
from vertagus.cli.options import configless_options
from vertagus.configuration import types as cfgtypes


@click.command("show-alias")
@click.argument("alias_name", required=True)
@click.option("--config", "-c", default=None, help="Path to the configuration file")
@configless_options
def show_alias_cmd(alias_name, config, **cli_opts):
    master_config = cli_utils.resolve_config(config, cli_opts, suppress_logging=True)
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
