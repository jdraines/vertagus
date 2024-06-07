import pytest
from unittest.mock import MagicMock, patch

from vertagus.providers.manifest.toml_manifest import TomlManifest


@pytest.fixture
def manifest_doc():
    return {
        "version": "1.0.0"
    }

@pytest.fixture(autouse=True)
def patch_load_doc(manifest_doc):
    with patch('vertagus.providers.manifest.toml_manifest.TomlManifest._load_doc', MagicMock(return_value=manifest_doc)):
        yield


def test_toml_manifest_version():
    manifest = TomlManifest("test", "test.toml", loc=["version"])
    assert manifest.version == "1.0.0"
    manifest_no_loc = TomlManifest("test", "test.toml")
    with pytest.raises(ValueError):
        manifest_no_loc.version
    manifest_invalid_loc = TomlManifest("test", "test.toml", loc=["invalid"])
    with pytest.raises(ValueError):
        manifest_invalid_loc.version

def test_full_path():
    manifest = TomlManifest("test", "test.toml")
    assert manifest._full_path() == "test.toml"
    manifest_root = TomlManifest("test", "test.toml", root="root")
    assert manifest_root._full_path() == "root/test.toml"