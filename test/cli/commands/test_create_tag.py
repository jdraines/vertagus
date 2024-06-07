import sys
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from vertagus.cli.commands import create_tag
from pathlib import Path
import yaml


_mock_configs_dir = Path(__file__).parent.parent.parent / "mock_docs" / "configs"
_mock_manifests_dir = Path(__file__).parent.parent.parent / "mock_docs" / "manifests"


def load_config(config_name):
    with open(_mock_configs_dir / config_name) as f:
        if config_name.endswith("yaml"):
            return yaml.safe_load(f)
        return f.read()


def load_manifest(manifest_name):
    with open(_mock_manifests_dir / manifest_name) as f:
        return f.read()


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def load_config_mock():
    with patch("vertagus.cli.commands.validate.load.load_config") as _load_config:
        yield _load_config


@pytest.fixture(autouse=True)
def mock_scm():
    with patch("vertagus.cli.commands.validate.factory.create_scm") as _scm_config:
        _mock_scm = MagicMock()
        _mock_scm.get_highest_version.return_value = "0.1.0"
        _scm_config.return_value = _mock_scm
        yield _mock_scm


@pytest.mark.parametrize(
    "config_name, manifest_name, manifest_type, expected_exit_code",
    [
        ("01-simple.yaml", "0.2.0.yaml", "yaml", 0),
    ],
)
def test_create_tag_simple(
    runner: CliRunner,
    config_name: str,
    manifest_name: str,
    manifest_type: str,
    expected_exit_code: int,
    load_config_mock: MagicMock,
):
    config = load_config(config_name)
    config["project"]["manifests"].append(
        {
            "name": manifest_name,
            "type": manifest_type,
            "path": str(_mock_manifests_dir / manifest_name),
            "loc": "project.version"
        }
    ) 
    load_config_mock.return_value = config
    result = runner.invoke(create_tag, ["--config", config_name])
    assert result.exit_code == expected_exit_code
