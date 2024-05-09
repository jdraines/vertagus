from unittest.mock import MagicMock
import pytest
from vertagus import factory
from vertagus.core.rule_bases import SingleVersionRule
from vertagus.configuration import types as t


class DummyManifest:
    def __init__(self, **kwargs):
        pass


    
@pytest.fixture
def mock_manifest_cls(monkeypatch):
    mock = MagicMock(return_value=DummyManifest)
    monkeypatch.setattr(factory, "get_manifest_cls", mock)
    return mock

def test_create_manifests(mock_manifest_cls):
    manifest_data_list = [t.ManifestData(name="test_manifest", type="dummy_type", path="test_path", loc=["1", "2"]),]

    result = factory.create_manifests(manifest_data_list, "root_path")

    # We verify that the 'get_manifest_cls' function was called with the correct arguments
    mock_manifest_cls.assert_called_with("dummy_type")

    # We verify that a list of ManifestBase instances is returned
    assert len(result) == len(manifest_data_list)
    for item in result:
        assert isinstance(item, DummyManifest)


@pytest.fixture
def mock_single_version_rules(monkeypatch):
    mock_rule_getter = MagicMock()
    monkeypatch.setattr(factory, "get_single_version_rules", mock_rule_getter)
    return mock_rule_getter

def test_create_single_version_rules(mock_single_version_rules):
    rule_names = ["rule1", "rule2", "rule3"]

    result = factory.create_single_version_rules(rule_names)

    # Verify that the 'get_single_version_rules' function was called with the correct arguments
    mock_single_version_rules.assert_called_with(rule_names)

    # We verify that a list of SingleVersionRule instances is returned
    for item in result:
        assert isinstance(item, SingleVersionRule)


@pytest.fixture
def mock_scm_data():
    return t.ScmData(root="root", type="dummy_type", **{"key": "value"})


def test_create_scm(mock_scm_data, monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(factory, "get_scm_cls", MagicMock(return_value=mock))
    result = factory.create_scm(mock_scm_data)
    factory.get_scm_cls.assert_called_with("dummy_type")
    mock.assert_called_with(root="root", key="value")
    assert result == mock.return_value


@pytest.fixture
def project_data():
    return t.ProjectData(
        manifests=[t.ManifestData(name="test_manifest", type="dummy_type", path="test_path", loc=["1", "2"])],
        rules=t.RulesData(current=["rule1", "rule2"], increment=["rule3"]),
        stages=[
            t.StageData(
                name="stage1",
                manifests=[t.ManifestData(name="test_manifest", type="dummy_type", path="test_path", loc=["1", "2"])],
                rules=t.RulesData(current=["rule1", "rule2"], increment=["rule3"])
            )],
        aliases=["alias1", "alias2"]
    )

