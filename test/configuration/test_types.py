import pytest
from unittest.mock import patch, mock_open

from vertagus.configuration import types as configtypes
from vertagus.configuration import load


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


def test_scm_data_with_branch_strategy():
    """Test ScmData can be created with branch-based strategy fields."""
    scm_data = configtypes.ScmData(
        type="git",
        version_strategy="branch",
        target_branch="main"
    )
    
    assert scm_data.scm_type == "git"
    assert scm_data.version_strategy == "branch"
    assert scm_data.target_branch == "main"


def test_scm_data_defaults_to_tag_strategy():
    """Test ScmData defaults to tag strategy when not specified."""
    scm_data = configtypes.ScmData(type="git")
    
    assert scm_data.scm_type == "git"
    assert scm_data.version_strategy == "tag"
    assert scm_data.target_branch is None


def test_scm_data_config_output_with_branch():
    """Test ScmData config method output with branch parameters."""
    scm_data = configtypes.ScmData(
        type="git",
        version_strategy="branch",
        target_branch="main",
        tag_prefix="v"
    )

    config_output = scm_data.config()

    assert config_output["version_strategy"] == "branch"
    assert config_output["target_branch"] == "main"
    assert config_output["tag_prefix"] == "v"
    assert "root" in config_output


def test_scm_data_config_excludes_none_target_branch():
    """Test ScmData config method when target_branch is None."""
    scm_data = configtypes.ScmData(type="git", version_strategy="tag")

    config_output = scm_data.config()

    assert config_output["version_strategy"] == "tag"
    assert "target_branch" not in config_output  # Should not be included when None


def test_load_config_with_branch_strategy():
    """Test loading configuration with branch-based strategy."""
    config_yaml = """
scm:
  type: git
  version_strategy: branch
  target_branch: main
manifests:
  - name: pyproject
    type: setuptools_pyproject
    path: pyproject.toml
    loc: project.version
"""

    with patch("builtins.open", mock_open(read_data=config_yaml)):
        with patch("os.path.exists", return_value=True):
            config = load.load_config("test_config.yaml")

    assert "scm" in config
    scm_config = config["scm"]
    assert scm_config["type"] == "git"
    assert scm_config["version_strategy"] == "branch"
    assert scm_config["target_branch"] == "main"


def test_load_config_without_branch_strategy():
    """Test loading configuration without branch strategy (should use defaults)."""
    config_yaml = """
scm:
  type: git
manifests:
  - name: pyproject
    type: setuptools_pyproject
    path: pyproject.toml
    loc: project.version
"""

    with patch("builtins.open", mock_open(read_data=config_yaml)):
        with patch("os.path.exists", return_value=True):
            config = load.load_config("test_config.yaml")

    assert "scm" in config
    scm_config = config["scm"]
    assert scm_config["type"] == "git"
    assert scm_config.get("version_strategy", "tag") == "tag"
    assert scm_config.get("target_branch") is None


def test_scm_data_with_manifest_configuration():
    """Test ScmData can be created with manifest configuration for branch strategy."""
    scm_data = configtypes.ScmData(
        type="git",
        version_strategy="branch",
        target_branch="main",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject"
    )
    
    assert scm_data.scm_type == "git"
    assert scm_data.version_strategy == "branch"
    assert scm_data.target_branch == "main"
    assert scm_data.manifest_path == "pyproject.toml"
    assert scm_data.manifest_type == "setuptools_pyproject"


def test_scm_data_config_with_manifest_info():
    """Test ScmData config method includes manifest configuration."""
    scm_data = configtypes.ScmData(
        type="git",
        version_strategy="branch",
        target_branch="main",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject",
        tag_prefix="v"
    )

    config_output = scm_data.config()

    assert config_output["version_strategy"] == "branch"
    assert config_output["target_branch"] == "main"
    assert config_output["manifest_path"] == "pyproject.toml"
    assert config_output["manifest_type"] == "setuptools_pyproject"
    assert config_output["tag_prefix"] == "v"
    assert "root" in config_output
