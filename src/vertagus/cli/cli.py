import logging
import os

logging.basicConfig(
    level=os.environ.get("VERTAGUS_LOG_LEVEL", "INFO"),
    format="{message}",
    style="{"
)


import click
from .commands import (
    validate_cmd,
    create_tag_cmd,
    create_aliases_cmd,
    list_rules_cmd,
    list_aliases_cmd,
    list_manifests_cmd,
    list_scms_cmd
)


@click.group()
def cli():
    pass


cli.add_command(validate_cmd)
cli.add_command(create_tag_cmd)
cli.add_command(create_aliases_cmd)
cli.add_command(list_rules_cmd)
cli.add_command(list_aliases_cmd)
cli.add_command(list_manifests_cmd)
cli.add_command(list_scms_cmd)
