import tomllib
from logging import getLogger

import yaml

from vertagus.utils.config import is_toml, is_yaml

from .types import MasterConfig

logger = getLogger(__name__)


def load_config(filepath: str, suppress_logging=False) -> MasterConfig:
    if not suppress_logging:
        logger.info(f"Loading configuration from {filepath}")
    with open(filepath, "rt") as f:
        doc = f.read()

    if is_yaml(doc):
        return yaml.safe_load(doc)
    elif is_toml(doc):
        return tomllib.loads(doc)
    else:
        raise ValueError(
            "Invalid configuration file format. Supported formats are YAML and TOML. "
            "If you are attempting to load one of these file types, you can receive a "
            "more detailed error message by ensuring that your configuration file uses "
            "the correct file extension."
        )
