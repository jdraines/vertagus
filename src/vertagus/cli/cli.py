import logging
import os

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="{message}",
    style="{"
)


import click
from .commands import (
    validate,
    create_tag
)


@click.group()
def cli():
    pass


cli.add_command(validate)
cli.add_command(create_tag)
