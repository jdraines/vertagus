import tomli
from .types import MasterConfig


def load_config(filepath: str) -> MasterConfig:
    with open(filepath, "rb") as f:
        return tomli.load(f)
