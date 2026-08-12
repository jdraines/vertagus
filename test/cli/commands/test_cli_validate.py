import sys
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from vertagus.cli.commands import validate_cmd
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
    with patch("vertagus.cli.commands.validate.cli_utils.load_config") as _load_config:
        yield _load_config


@pytest.fixture(autouse=True)
def mock_scm():
    with patch("vertagus.factory.create_scm") as _scm_config:
        _mock_scm = MagicMock()
        _mock_scm.get_highest_version.return_value = "0.1.0"
        _scm_config.return_value = _mock_scm
        yield _mock_scm


@pytest.mark.parametrize(
    "config_name, manifest_name, manifest_type, expected_exit_code",
    [
        ("01-simple.yaml", "0.2.0.yaml", "yaml", 0),
        ("01-simple.yaml", "0.1.0.yaml", "yaml", 1)
    ],
)
def test_validate_simple(
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
    result = runner.invoke(validate_cmd, ["--config", config_name])
    assert result.exit_code == expected_exit_code


@pytest.mark.parametrize(
    "manifest_name, expected_exit_code",
    [
        ("0.2.0.yaml", 0),
        ("0.1.0.yaml", 1),
    ],
)
def test_validate_without_a_config_file(runner: CliRunner, manifest_name: str, expected_exit_code: int):
    result = runner.invoke(
        validate_cmd,
        [
            "--manifest",
            f"path={_mock_manifests_dir / manifest_name},type=yaml,loc=project.version",
            "--rule",
            "not_empty",
            "--rule",
            "any_increment",
        ],
    )
    assert result.exit_code == expected_exit_code


def test_validate_without_a_config_file_ignores_a_config_file_in_the_cwd(runner: CliRunner, load_config_mock):
    runner.invoke(
        validate_cmd,
        ["--manifest", f"path={_mock_manifests_dir / '0.2.0.yaml'},type=yaml,loc=project.version"],
    )
    load_config_mock.assert_not_called()


def test_validate_cli_options_override_a_config_file(runner: CliRunner, load_config_mock):
    config = load_config("01-simple.yaml")
    config["project"]["manifests"] = [
        {
            "name": "0.1.0.yaml",
            "type": "yaml",
            "path": str(_mock_manifests_dir / "0.1.0.yaml"),
            "loc": "project.version",
        }
    ]
    load_config_mock.return_value = config

    # The configured manifest is behind the mocked SCM version, so validation only passes
    # if the manifest named on the command line replaced it.
    result = runner.invoke(
        validate_cmd,
        [
            "--config",
            "01-simple.yaml",
            "--manifest",
            f"path={_mock_manifests_dir / '0.2.0.yaml'},type=yaml,loc=project.version",
        ],
    )
    assert result.exit_code == 0


def test_validate_rejects_a_stage_name_without_a_config_file(runner: CliRunner):
    result = runner.invoke(
        validate_cmd,
        ["--manifest", f"path={_mock_manifests_dir / '0.2.0.yaml'},type=yaml", "--stage-name", "dev"],
    )
    assert result.exit_code != 0


def test_validate_print_config(runner: CliRunner):
    result = runner.invoke(
        validate_cmd,
        ["--manifest", f"path={_mock_manifests_dir / '0.2.0.yaml'},type=yaml", "--print-config", "--tag-prefix", "v"],
    )
    assert result.exit_code == 0
    assert "tag_prefix: v" in result.output
