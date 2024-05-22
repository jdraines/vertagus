import typing as T
from .setuptools_ import SetuptoolsPyprojectManifest
from .json_manifest import JsonManifest
from .yaml_manifest import YamlManifest

_manifest_types = {
    SetuptoolsPyprojectManifest.manifest_type: SetuptoolsPyprojectManifest,
    JsonManifest.manifest_type: JsonManifest,
    YamlManifest.manifest_type: YamlManifest,
}


def get_manifest_cls(manifest_type: str) -> T.Type[SetuptoolsPyprojectManifest]:
    if manifest_type not in _manifest_types:
        raise ValueError(f"Unknown manifest type: {manifest_type}")
    return _manifest_types[manifest_type]


def register_manifest_cls(manifest_cls: T.Type[SetuptoolsPyprojectManifest]):
    _manifest_types[manifest_cls.manifest_type] = manifest_cls
