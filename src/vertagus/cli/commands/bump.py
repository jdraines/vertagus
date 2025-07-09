import os
from pathlib import Path
import sys

import click

from vertagus.configuration import load
from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops
from vertagus.core.project import NoBumperDefinedError
from vertagus.core.bumper_base import BumperException

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


@click.command(
    "bump",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
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
@click.option(
    "--scm-branch",
    "-b",
    default=None,
    help="Optional SCM branch to validate against. Defaults to configured branch."
)
@click.option(
    "--no-write",
    "-n",
    is_flag=True,
    default=False,
    help="If set, the version will not be written to the manifest files."
)
def bump_cmd(context, config, stage_name, scm_branch, no_write):
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
    try:
        new_version = ops.bump_version(
            scm=scm,
            project=project,
            stage_name=stage_name,
            write=not no_write,
            bumper_args=context.args
        )
    except NoBumperDefinedError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)
    except BumperException as e:
        click.echo(click.style(f"{e.__class__.__name__}: {e}", fg="red"), err=True)
        sys.exit(1)
    
    except Exception as e:
        click.echo(click.style(f"An unexpected error occurred: {e}", fg="red"), err=True)
        sys.exit(1)

    if not new_version:
        click.echo("No version was bumped.")
        sys.exit(1)
    else:
        click.echo(f"Version bumped to: {new_version}")
        sys.exit(0)
