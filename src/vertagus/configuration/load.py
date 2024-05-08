import yaml
import tomli
from .types import MasterConfig
from vertagus.utils.config import is_yaml, is_toml


def load_config(filepath: str) -> MasterConfig:

    with open(filepath, "rt") as f:
        doc = f.read()

    if is_yaml(doc):
        return yaml.safe_load(doc)
    elif is_toml(doc):
        return tomli.loads(doc)
    else:
        raise ValueError(
            "Invalid configuration file format. Supported formats are YAML and TOML. "
            "If you are attempting to load one of these file types, you can receive a "
            "more detailed error message by ensuring that your configuration file uses "
            "the correct file extension."
        )
