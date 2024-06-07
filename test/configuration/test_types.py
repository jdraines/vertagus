import pytest

from vertagus.configuration import types as configtypes


def test_manifest_data():
    data = configtypes.ManifestData(
        name="test_manifest",
        type="dummy_type",
        path="test_path",
        loc=["project", "version"]
    )

    assert data.name == "test_manifest"
    assert data.type == "dummy_type"
    assert data.path == "test_path"
    assert data.loc == ["project", "version"]

    data_locstring = configtypes.ManifestData(
        name="test_manifest",
        type="dummy_type",
        path="test_path",
        loc="project.version"
    )
    assert data_locstring.loc == ["project", "version"]
