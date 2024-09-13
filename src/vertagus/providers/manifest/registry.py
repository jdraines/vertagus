import typing as T
from vertagus.core.manifest_base import ManifestBase
from .setuptools_ import SetuptoolsPyprojectManifest
from .json_manifest import JsonManifest
from .yaml_manifest import YamlManifest
from .toml_manifest import TomlManifest

_manifest_types = {
    SetuptoolsPyprojectManifest.manifest_type: SetuptoolsPyprojectManifest,
    JsonManifest.manifest_type: JsonManifest,
    YamlManifest.manifest_type: YamlManifest,
    TomlManifest.manifest_type: TomlManifest,
}


def get_manifest_cls(manifest_type: str) -> T.Type[ManifestBase]:
    if manifest_type not in _manifest_types:
        raise ValueError(f"Unknown manifest type: {manifest_type}")
    return _manifest_types[manifest_type]


def register_manifest_cls(manifest_cls: T.Type[ManifestBase]):
    _manifest_types[manifest_cls.manifest_type] = manifest_cls


def list_manifest_types() -> list[T.Type[ManifestBase]]:
    return sorted(list(_manifest_types.values()), key=lambda x: x.manifest_type)
