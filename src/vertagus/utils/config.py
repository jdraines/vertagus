from logging import getLogger
import yaml
import tomllib

logger = getLogger(__name__)


def is_yaml(doc, filepath: str = None) -> bool:
    try:
        yaml.safe_load(doc)
        return True
    except yaml.YAMLError as e:
        if filepath and any([filepath.endswith(ext) for ext in [".yaml", ".yml"]]):
            raise e
        return False


def is_toml(doc: str, filepath: str = None) -> bool:
    try:
        tomllib.loads(doc)
        return True
    except tomllib.TOMLDecodeError as e:
        if filepath and filepath.endswith(".toml"):
            raise e
        return False
