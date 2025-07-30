from typing import Optional
import click
import sys
import os
from pathlib import Path
from vertagus.configuration import load
from vertagus.configuration import types as cfgtypes


def get_cwd() -> Path:
    return Path(os.getcwd())


def validate_config_path(config_path: Optional[str]) -> str:
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


def load_config(config_path: Optional[str], suppress_logging=False) -> cfgtypes.MasterConfig:
    config_path = validate_config_path(config_path)
    master_config = load.load_config(config_path, suppress_logging)
    default_package_root = str(Path(config_path).parent)
    if "root" not in master_config["project"]:
        master_config["project"]["root"] = default_package_root
    return master_config
