import os
from pathlib import Path
import sys

import click

from vertagus.configuration import load
from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops

_cwd = Path(os.getcwd())


def _try_get_config_path_in_cwd():
    if "vertagus.toml" in os.listdir(_cwd):
        return str(_cwd / "vertagus.toml")
    elif "vertagus.yml" in os.listdir(_cwd):
        return str(_cwd / "vertagus.yml")
    elif "vertagus.yaml" in os.listdir(_cwd):
        return str(_cwd / "vertagus.yaml")
    else:
        return None


@click.command("validate")
@click.option(
    "--config", 
    "-c", 
    default=None, 
    help="Path to the configuration file"
)
@click.option(
    "--stage-name",
    "-s",
    default=None,
    help="Name of a stage"
)
def validate_cmd(config, stage_name):
    if not config:
        config = _try_get_config_path_in_cwd()
    master_config = load.load_config(config)
    scm = factory.create_scm(
        cfgtypes.ScmData(**master_config["scm"])
    )
    default_package_root = Path(config).parent
    if "root" not in master_config["project"]:
        master_config["project"]["root"] = default_package_root
    project = factory.create_project(
        cfgtypes.ProjectData.from_project_config(master_config["project"])
    )
    if not ops.validate_project_version(
        scm=scm,
        project=project,
        stage_name=stage_name
    ):
        sys.exit(1)
