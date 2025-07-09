import pytest
from unittest.mock import MagicMock, patch

from vertagus.providers.manifest.json_manifest import JsonManifest


@pytest.fixture
def manifest_doc():
    return {
        "version": "1.0.0"
    }

@pytest.fixture(autouse=True)
def patch_load_doc(manifest_doc):
    with patch('vertagus.providers.manifest.json_manifest.JsonManifest._load_doc', MagicMock(return_value=manifest_doc)):
        yield


def test_json_manifest_version():
    manifest = JsonManifest("test", "test.json", loc=["version"])
    assert manifest.version == "1.0.0"
    manifest_no_loc = JsonManifest("test", "test.json")
    with pytest.raises(ValueError):
        manifest_no_loc.version
    manifest_invalid_loc = JsonManifest("test", "test.json", loc=["invalid"])
    with pytest.raises(ValueError):
        manifest_invalid_loc.version

def test_full_path():
    manifest = JsonManifest("test", "test.json")
    assert manifest._full_path() == "test.json"
    manifest_root = JsonManifest("test", "test.json", root="root")
    assert manifest_root._full_path() == "root/test.json"


def test_update_version():
    manifest = JsonManifest("test", "test.json", loc=["version"])
    assert manifest.version == "1.0.0"
    manifest.update_version("2.0.0", write=False)
    assert manifest.version == "2.0.0"
