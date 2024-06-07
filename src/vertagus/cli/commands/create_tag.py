import os
from pathlib import Path

import click

from vertagus.configuration import load
from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops


@click.command(name="create-tag")
@click.option(
    "--config", 
    "-c", 
    default=str(Path(os.getcwd()) / "vertagus.toml"), 
    help="Path to the configuration file"
)
@click.option(
    "--stage-name",
    "-s",
    default=None,
    help="Name of a stage"
)
@click.option(
    "--ref",
    "-r",
    default=None,
    help="An SCM ref that should be tagged. Default is current commit."
)
def create_tag_cmd(config, stage_name, ref):
    master_config = load.load_config(config)
    scm = factory.create_scm(
        data=cfgtypes.ScmData(**master_config["scm"])
    )
    default_package_root = Path(config).parent
    if "root" not in master_config["project"]:
        master_config["project"]["root"] = default_package_root
    project = factory.create_project(
        cfgtypes.ProjectData.from_project_config(master_config["project"]),
    )
    return ops.create_tags(
        scm=scm,
        project=project,
        stage_name=stage_name,
        ref=ref
    )
