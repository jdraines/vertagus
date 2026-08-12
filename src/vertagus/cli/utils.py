import click
import sys
import os
from pathlib import Path

import yaml

from vertagus.configuration import from_cli
from vertagus.configuration import load
from vertagus.configuration import types as cfgtypes
from vertagus.errors import ConfigurationError


def get_cwd() -> Path:
    return Path(os.getcwd())


def validate_config_path(config_path: str | None) -> str:
    if not config_path:
        config_path = _try_get_config_path_in_cwd()
    if not config_path:
        click.echo(click.style("Error: No configuration file found in the current directory.", fg="red"), err=True)
        sys.exit(1)
    return config_path


def _try_get_config_path_in_cwd():
    _cwd = get_cwd()
    if "vertagus.toml" in os.listdir(_cwd):
        return str(_cwd / "vertagus.toml")
    elif "vertagus.yml" in os.listdir(_cwd):
        return str(_cwd / "vertagus.yml")
    elif "vertagus.yaml" in os.listdir(_cwd):
        return str(_cwd / "vertagus.yaml")
    else:
        return None


def load_config(config_path: str | None, suppress_logging=False) -> cfgtypes.MasterConfig:
    config_path = validate_config_path(config_path)
    master_config = load.load_config(config_path, suppress_logging)
    default_package_root = str(Path(config_path).parent)
    if "root" not in master_config["project"]:
        master_config["project"]["root"] = default_package_root
    return master_config


def resolve_config(
    config_path: str | None,
    cli_opts: dict | None = None,
    stage_name: str | None = None,
    suppress_logging: bool = False,
) -> cfgtypes.MasterConfig:
    """Resolve the configuration a command should run with.

    With no configuration options on the command line, this behaves exactly like
    :func:`load_config`. Otherwise the options either overlay a configuration file, when
    one was named with ``--config``, or stand in for it entirely. In the latter case no
    configuration file is discovered in the current directory, so that an ad hoc
    invocation cannot silently pick up settings the user did not ask for.
    """
    cli_opts = dict(cli_opts or {})
    print_config = cli_opts.pop("print_config", False)
    opts = from_cli.CliConfigOptions(**cli_opts)

    if not opts.any_provided():
        master_config = load_config(config_path, suppress_logging or print_config)
    elif config_path:
        master_config = from_cli.merge_config(load_config(config_path, suppress_logging or print_config), opts)
    else:
        if stage_name:
            raise ConfigurationError(
                f"Cannot use --stage-name {stage_name!r} without a configuration file: stages are "
                "defined in a vertagus configuration file. Pass --config, or configure the stage's "
                "rules directly with --rule."
            )
        master_config = from_cli.build_master_config(opts)

    if print_config:
        echo_config_and_exit(master_config)
    return master_config


def echo_config_and_exit(master_config: cfgtypes.MasterConfig) -> None:
    """Print a resolved configuration as YAML and exit successfully."""
    click.echo(yaml.dump(dict(master_config), default_flow_style=False, sort_keys=False))
    sys.exit(0)
