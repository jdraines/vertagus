from unittest.mock import MagicMock, patch
import pytest
import os
from vertagus import factory
from vertagus.core.rule_bases import SingleVersionRule
from vertagus.configuration import types as t
from vertagus.core.scm_base import ScmBase


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

@pytest.fixture
def mock_scm_cls():
    class MockScm(ScmBase):
        def __init__(self,
                    root: str = None,
                    tag_prefix: str = None,
                    user_data: dict = None,
                    remote_name: str = None,
                    **kwargs
                    ):
            self.root = root or os.getcwd()
            self.tag_prefix = tag_prefix
            self.user_data = user_data 
            self.remote_name = remote_name

        def create_tag(self, tag, ref: str=None):
            pass
        
        def delete_tag(self, tag_name: str):
            pass
        
        def list_tags(self, prefix: str=None):
            return ["tag1", "tag2", "tag3"]

        def get_highest_version(self, prefix: str=None):
            pass

        def migrate_alias(self, alias: str, ref: str = None):
            pass

    return MockScm

def test_create_scm(mock_scm_data, mock_scm_cls, monkeypatch):
    monkeypatch.setattr(factory, "get_scm_cls", MagicMock(return_value=mock_scm_cls))
    scm = factory.create_scm(mock_scm_data)
    factory.get_scm_cls.assert_called_with("dummy_type")
    assert scm.root == "root"
    assert scm.tag_prefix is None


def test_create_scm_with_branch_strategy():
    """Test creating SCM instance with branch strategy."""
    branch_scm_data = t.ScmData(
        type="git",
        root="/test/path",
        version_strategy="branch",
        target_branch="main",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject",
        tag_prefix="v"
    )
    
    mock_scm_class = MagicMock(spec=ScmBase)
    
    with patch('vertagus.factory.get_scm_cls') as mock_get_scm_cls:
        mock_get_scm_cls.return_value = mock_scm_class
        
        factory.create_scm(branch_scm_data)
        
        # Verify the correct SCM class was requested
        mock_get_scm_cls.assert_called_once_with("git")
        
        # Verify the SCM was instantiated with correct parameters including manifest info
        mock_scm_class.assert_called_once_with(
            root="/test/path",
            version_strategy="branch",
            target_branch="main",
            manifest_path="pyproject.toml",
            manifest_type="setuptools_pyproject",
            tag_prefix="v"
        )


def test_create_scm_with_tag_strategy():
    """Test creating SCM instance with tag strategy (default)."""
    tag_scm_data = t.ScmData(
        type="git",
        root="/test/path",
        version_strategy="tag",
        tag_prefix="v"
    )
    
    mock_scm_class = MagicMock(spec=ScmBase)
    
    with patch('vertagus.factory.get_scm_cls') as mock_get_scm_cls:
        mock_get_scm_cls.return_value = mock_scm_class
        
        factory.create_scm(tag_scm_data)
        
        # Verify the correct SCM class was requested
        mock_get_scm_cls.assert_called_once_with("git")
        
        # Verify the SCM was instantiated with correct parameters
        mock_scm_class.assert_called_once_with(
            root="/test/path",
            version_strategy="tag",
            tag_prefix="v"
        )


def test_scm_data_config_includes_branch_parameters():
    """Test that ScmData.config() includes branch-related parameters."""
    branch_scm_data = t.ScmData(
        type="git",
        root="/test/path",
        version_strategy="branch",
        target_branch="main",
        tag_prefix="v"
    )
    
    config = branch_scm_data.config()
    
    assert config["version_strategy"] == "branch"
    assert config["target_branch"] == "main"
    assert config["root"] == "/test/path"
    assert config["tag_prefix"] == "v"


def test_scm_data_config_excludes_none_target_branch():
    """Test that ScmData.config() excludes target_branch when None."""
    tag_scm_data = t.ScmData(
        type="git",
        root="/test/path",
        version_strategy="tag",
        tag_prefix="v"
    )
    
    config = tag_scm_data.config()
    
    assert config["version_strategy"] == "tag"
    assert "target_branch" not in config
    assert config["root"] == "/test/path"


def test_scm_data_config_includes_manifest_parameters():
    """Test that ScmData.config() includes manifest-related parameters."""
    branch_scm_data = t.ScmData(
        type="git",
        root="/test/path",
        version_strategy="branch",
        target_branch="main",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject",
        tag_prefix="v"
    )
    
    config = branch_scm_data.config()
    
    assert config["version_strategy"] == "branch"
    assert config["target_branch"] == "main"
    assert config["manifest_path"] == "pyproject.toml"
    assert config["manifest_type"] == "setuptools_pyproject"
    assert config["root"] == "/test/path"
    assert config["tag_prefix"] == "v"


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

