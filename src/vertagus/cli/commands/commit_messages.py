import os
from pathlib import Path
import sys

import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops
from vertagus.cli import utils as cli_utils


@click.command("commits")
@click.option(
    "--config", 
    "-c", 
    default=None, 
    help="Path to the configuration file"
)
@click.option(
    "--scm-branch",
    "-b",
    default=None,
    help="Optional SCM branch to validate against. Defaults to configured branch."
)
def commit_messages_cmd(config, scm_branch):
    master_config = cli_utils.load_config(config)
    scm = factory.create_scm(
        cfgtypes.ScmData(**master_config["scm"])
    )
    highest_version = scm.get_highest_version(
        prefix=master_config["scm"].get("tag_prefix"),
        branch=scm_branch
    )
    msgs = scm.get_commit_messages_since_highest_version(
        prefix=master_config["scm"].get("tag_prefix"),
        branch=scm_branch
    )
    print(f"Commit messages since highest version {highest_version}:")
    for msg in msgs:
        print(f" - {msg}")
