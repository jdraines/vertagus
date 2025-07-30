import sys

import click

from vertagus.configuration import types as cfgtypes
from vertagus import factory
from vertagus import operations as ops
from vertagus.core.project import NoBumperDefinedError
from vertagus.core.bumper_base import BumperException
from vertagus.cli import utils as cli_utils


@click.command(
    "bump",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.pass_context
@click.option("--config", "-c", default=None, help="Path to the configuration file")
@click.option("--stage-name", "-s", default=None, help="Name of a stage")
@click.option(
    "--no-write",
    "-n",
    is_flag=True,
    default=False,
    help="If set, the version will not be written to the manifest files.",
)
def bump_cmd(context, config, stage_name, no_write):
    master_config = cli_utils.load_config(config)
    project = factory.create_project(cfgtypes.ProjectData.from_project_config(master_config["project"]))
    bumper_kwargs = _parse_context_args_to_kwargs(context.args)
    scm = factory.create_scm(cfgtypes.ScmData(**master_config["scm"]))
    try:
        new_version = ops.bump_version(
            scm=scm, project=project, stage_name=stage_name, write=not no_write, bumper_kwargs=bumper_kwargs
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


class BumperArgumentInvalidFormat(BumperException):
    pass


def _parse_context_args_to_kwargs(args) -> dict[str, str]:
    """
    Parse context args to kwargs for the bump command.
    """
    kwargs = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            kwargs[key] = value
        else:
            if len(kwargs) == 0:
                kwargs["level"] = arg  # Maintain backward compatibility for 0.2.4
            else:
                raise BumperArgumentInvalidFormat(f"Invalid argument format: {arg}. Expected 'key=value'.")
    return kwargs
