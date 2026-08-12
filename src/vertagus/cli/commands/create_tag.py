import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops
from vertagus.cli import utils as cli_utils
from vertagus.cli.options import configless_options


@click.command(name="create-tag")
@click.option("--config", "-c", default=None, help="Path to the configuration file")
@click.option("--stage-name", "-s", default=None, help="Name of a stage")
@click.option("--ref", "-r", default=None, help="An SCM ref that should be tagged. Default is current commit.")
@configless_options
def create_tag_cmd(config, stage_name, ref, **cli_opts):
    master_config = cli_utils.resolve_config(config, cli_opts, stage_name=stage_name)
    scm = factory.create_scm(data=cfgtypes.ScmData(**master_config["scm"]))
    project = factory.create_project(
        cfgtypes.ProjectData.from_project_config(master_config["project"]),
    )
    return ops.create_tags(scm=scm, project=project, stage_name=stage_name, ref=ref)
