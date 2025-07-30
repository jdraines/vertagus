import sys

import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops
from vertagus.cli import utils as cli_utils


@click.command("validate")
@click.option("--config", "-c", default=None, help="Path to the configuration file")
@click.option("--stage-name", "-s", default=None, help="Name of a stage")
@click.option(
    "--scm-branch", "-b", default=None, help="Optional SCM branch to validate against. Defaults to configured branch."
)
def validate_cmd(config, stage_name, scm_branch):
    master_config = cli_utils.load_config(config)
    scm = factory.create_scm(cfgtypes.ScmData(**master_config["scm"]))
    project = factory.create_project(cfgtypes.ProjectData.from_project_config(master_config["project"]))
    if not ops.validate_project_version(scm=scm, project=project, stage_name=stage_name, scm_branch=scm_branch):
        sys.exit(1)
