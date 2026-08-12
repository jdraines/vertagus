import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

import yaml

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
    assert manifest_root._full_path() == str(Path("root/test.yaml"))


def test_update_version():
    manifest = YamlManifest("test", "test.yaml", loc=["version"])
    assert manifest.version == "1.0.0"
    manifest.update_version("2.0.0", write=False)
    assert manifest.version == "2.0.0"


_MANIFEST = """\
# The package
project:
  name: pkg  # its name
  version: 1.0.0

  deps:
    - click  # the CLI framework
"""


@pytest.fixture
def yaml_file(tmp_path, patch_load_doc):
    path = tmp_path / "manifest.yaml"
    path.write_text(_MANIFEST)
    return path


def test_update_version_preserves_comments_and_formatting(yaml_file):
    manifest = YamlManifest("test", str(yaml_file), loc=["project", "version"])
    manifest._doc = {"project": {"name": "pkg", "version": "1.0.0", "deps": ["click"]}}

    manifest.update_version("2.0.0")

    assert yaml_file.read_text() == _MANIFEST.replace("version: 1.0.0", "version: '2.0.0'")


def test_update_version_falls_back_to_a_full_rewrite(yaml_file, caplog):
    # The version is absent from the file, so it cannot be replaced in place.
    yaml_file.write_text("project:\n  name: pkg\n")
    manifest = YamlManifest("test", str(yaml_file), loc=["project", "version"])
    manifest._doc = {"project": {"name": "pkg"}}

    manifest.update_version("2.0.0")

    assert yaml.safe_load(yaml_file.read_text())["project"]["version"] == "2.0.0"
    assert "may not be preserved" in caplog.text


def test_update_version_leaves_the_file_alone_when_not_writing(yaml_file):
    manifest = YamlManifest("test", str(yaml_file), loc=["project", "version"])
    manifest._doc = {"project": {"version": "1.0.0"}}

    manifest.update_version("2.0.0", write=False)

    assert yaml_file.read_text() == _MANIFEST
