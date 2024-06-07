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
    create_tag,
    create_aliases,
    list_rules
)


@click.group()
def cli():
    pass


cli.add_command(validate_cmd)
cli.add_command(create_tag)
cli.add_command(create_aliases)
cli.add_command(list_rules)
