import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

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
    assert manifest_root._full_path() == str(Path("root/test.toml"))

def test_update_version():
    manifest = TomlManifest("test", "test.toml", loc=["version"])
    assert manifest.version == "1.0.0"
    manifest.update_version("2.0.0", write=False)
    assert manifest.version == "2.0.0"


_PYPROJECT = '''\
# The build system
[build-system]
requires = ["setuptools"]  # keep it minimal

[project]
name = "pkg"
version = "1.0.0"
dependencies = [
    "click",  # the CLI framework
]
'''


@pytest.fixture
def toml_file(tmp_path, patch_load_doc):
    path = tmp_path / "pyproject.toml"
    path.write_text(_PYPROJECT)
    return path


def test_update_version_preserves_comments_and_formatting(toml_file):
    manifest = TomlManifest("test", str(toml_file), loc=["project", "version"])
    manifest._doc = {"project": {"version": "1.0.0"}, "build-system": {"requires": ["setuptools"]}}

    manifest.update_version("2.0.0")

    assert toml_file.read_text() == _PYPROJECT.replace('version = "1.0.0"', 'version = "2.0.0"')


def test_update_version_falls_back_to_a_full_rewrite(toml_file, caplog):
    # The version is absent from the file, so it cannot be replaced in place.
    toml_file.write_text('[project]\nname = "pkg"\n')
    manifest = TomlManifest("test", str(toml_file), loc=["project", "version"])
    manifest._doc = {"project": {"name": "pkg"}}

    manifest.update_version("2.0.0")

    assert 'version = "2.0.0"' in toml_file.read_text()
    assert "may not be preserved" in caplog.text


def test_update_version_leaves_the_file_alone_when_not_writing(toml_file):
    manifest = TomlManifest("test", str(toml_file), loc=["project", "version"])
    manifest._doc = {"project": {"version": "1.0.0"}}

    manifest.update_version("2.0.0", write=False)

    assert toml_file.read_text() == _PYPROJECT
