from unittest.mock import MagicMock
import pytest

from vertagus.providers.manifest.setuptools_ import pyproject_manifest as spm


@pytest.fixture
def manifest_doc():
    return {
        "project": {
            "version": "1.0.0"
        }
    }


@pytest.fixture
def manifest(monkeypatch, manifest_doc):
    load_doc = MagicMock(return_value=manifest_doc)
    monkeypatch.setattr(spm.SetuptoolsPyprojectManifest, "_load_doc", load_doc)
    return spm.SetuptoolsPyprojectManifest("test", "/tmp/test.toml")


def test_init(manifest, manifest_doc):
    assert manifest.name == "test"
    assert manifest.path == "/tmp/test.toml"
    assert manifest.loc == ["project", "version"]
    assert manifest._doc == manifest_doc


def test_version(manifest):
    assert manifest.version == "1.0.0"
