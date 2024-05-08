import os
from pathlib import Path
import sys

import click

from vertagus.configuration import load
from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops

_cwd = Path(os.getcwd())


@click.command()
@click.option(
    "--config", 
    "-c", 
    default=str(_cwd / "vertagus.toml"), 
    help="Path to the configuration file"
)
@click.option(
    "--stage-name",
    "-s",
    default=None,
    help="Name of a stage"
)
def validate(config, stage_name):
    master_config = load.load_config(config)
    root = master_config["scm"].pop("root", Path(config).parent)
    scm = factory.create_scm(
        root,
        cfgtypes.ScmData(**master_config["scm"])
    )
    project = factory.create_project(
        cfgtypes.ProjectData.from_project_config(master_config["project"]),
        root=root
    )
    if not ops.validate_project_version(
        scm=scm,
        project=project,
        stage_name=stage_name
    ):
        sys.exit(1)
