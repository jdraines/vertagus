import tomli
from ._types import MasterConfig


def load_config(filepath: str) -> MasterConfig:
    with open(filepath, "r") as f:
        return tomli.load(f)
