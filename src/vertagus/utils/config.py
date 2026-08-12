import tomllib
from logging import getLogger

import yaml

logger = getLogger(__name__)


def is_yaml(doc, filepath: str | None = None) -> bool:
    try:
        yaml.safe_load(doc)
        return True
    except yaml.YAMLError:
        if filepath and filepath.endswith((".yaml", ".yml")):
            raise
        return False


def is_toml(doc: str, filepath: str | None = None) -> bool:
    try:
        tomllib.loads(doc)
        return True
    except tomllib.TOMLDecodeError:
        if filepath and filepath.endswith(".toml"):
            raise
        return False
