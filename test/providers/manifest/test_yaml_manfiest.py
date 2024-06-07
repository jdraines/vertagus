import pytest
from unittest.mock import MagicMock, patch

from vertagus.providers.manifest.yaml_manifest import YamlManifest


@pytest.fixture
def manifest_doc():
    return {
        "version": "1.0.0"
    }

@pytest.fixture(autouse=True)
def patch_load_doc(manifest_doc):
    with patch('vertagus.providers.manifest.yaml_manifest.YamlManifest._load_doc', MagicMock(return_value=manifest_doc)):
        yield


def test_yaml_manifest_version():
    manifest = YamlManifest("test", "test.yaml", loc=["version"])
    assert manifest.version == "1.0.0"
    manifest_no_loc = YamlManifest("test", "test.yaml")
    with pytest.raises(ValueError):
        manifest_no_loc.version
    manifest_invalid_loc = YamlManifest("test", "test.yaml", loc=["invalid"])
    with pytest.raises(ValueError):
        manifest_invalid_loc.version


def test_full_path():
    manifest = YamlManifest("test", "test.yaml")
    assert manifest._full_path() == "test.yaml"
    manifest_root = YamlManifest("test", "test.yaml", root="root")
    assert manifest_root._full_path() == "root/test.yaml"