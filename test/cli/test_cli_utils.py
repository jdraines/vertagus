from pathlib import Path
import pytest
import yaml
from unittest.mock import patch, MagicMock

from vertagus.cli import utils as cli_utils
from vertagus.errors import ConfigurationError


@patch("vertagus.cli.utils.os.getcwd")
def test_get_cwd(mock_getcwd):
    mock_getcwd.return_value = "/mock/path"
    cwd = cli_utils.get_cwd()
    assert cwd == Path("/mock/path")
    mock_getcwd.assert_called_once()


@patch("vertagus.cli.utils.os.getcwd")
def test__try_get_config_path_in_cwd(mock_getcwd):
    mock_getcwd.return_value = "/mock/path"
    with patch("vertagus.cli.utils.os.listdir") as mock_listdir:
        mock_listdir.return_value = ["vertagus.toml"]
        config_path = cli_utils._try_get_config_path_in_cwd()
        assert config_path == str(Path("/mock/path") / "vertagus.toml")

        mock_listdir.return_value = ["vertagus.yml"]
        config_path = cli_utils._try_get_config_path_in_cwd()
        assert config_path == str(Path("/mock/path") / "vertagus.yml")

        mock_listdir.return_value = ["vertagus.yaml"]
        config_path = cli_utils._try_get_config_path_in_cwd()
        assert config_path == str(Path("/mock/path") / "vertagus.yaml")

        mock_listdir.return_value = []
        config_path = cli_utils._try_get_config_path_in_cwd()
        assert config_path is None

@patch("vertagus.cli.utils.validate_config_path")
@patch("vertagus.cli.utils.load.load_config")
def test_load_config(mock_load_config, mock_validate_config_path):
    mock_validate_config_path.return_value = str(Path("/my/config/path.yaml"))
    mock_load_config.return_value = {"project": {"root": str(Path("/mock/root"))}}

    config = cli_utils.load_config(None)    
    mock_validate_config_path.assert_called_once_with(None)
    mock_load_config.assert_called_once_with(str(Path("/my/config/path.yaml")), False)
    assert config == {"project": {"root": str(Path("/mock/root"))}}

    mock_load_config.return_value = {"project": {}}
    config = cli_utils.load_config(None)
    assert config == {"project": {"root": str(Path("/my/config"))}}


@patch("vertagus.cli.utils.load_config")
def test_resolve_config_without_cli_options_loads_a_file(mock_load_config):
    mock_load_config.return_value = {"project": {}, "scm": {}}

    config = cli_utils.resolve_config("some/config.yaml", {})

    mock_load_config.assert_called_once_with("some/config.yaml", False)
    assert config == {"project": {}, "scm": {}}


@patch("vertagus.cli.utils.load_config")
def test_resolve_config_merges_cli_options_onto_a_file(mock_load_config):
    mock_load_config.return_value = {"project": {"rules": ["not_empty"]}, "scm": {"type": "git"}}

    config = cli_utils.resolve_config("some/config.yaml", {"rule": ("any_increment",), "tag_prefix": "v"})

    assert config["project"]["rules"] == ["any_increment"]
    assert config["scm"]["tag_prefix"] == "v"


@patch("vertagus.cli.utils.load_config")
def test_resolve_config_from_cli_options_alone_ignores_config_files(mock_load_config, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vertagus.yaml").write_text("project: {}\n")

    config = cli_utils.resolve_config(None, {"manifest": ("pyproject.toml",), "rule": ("not_empty",)})

    mock_load_config.assert_not_called()
    assert config["project"]["manifests"][0]["path"] == str(tmp_path / "pyproject.toml")
    assert config["scm"] == {"type": "git"}


def test_resolve_config_rejects_a_stage_name_without_a_config_file():
    with pytest.raises(ConfigurationError, match="Cannot use --stage-name"):
        cli_utils.resolve_config(None, {"manifest": ("pyproject.toml",)}, stage_name="dev")


def test_resolve_config_print_config_exits(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        cli_utils.resolve_config(None, {"manifest": ("pyproject.toml",), "print_config": True})

    assert excinfo.value.code == 0
    assert "manifests:" in capsys.readouterr().out


def test_print_config_output_can_be_saved_as_a_config_file(capsys, tmp_path, monkeypatch):
    """The documented `--print-config > vertagus.yaml` recipe has to produce a file that
    still works after the checkout moves, so paths come back out relative."""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit):
        cli_utils.resolve_config(
            None, {"manifest": ("sub/pyproject.toml",), "rule": ("not_empty",), "print_config": True}
        )

    printed = yaml.safe_load(capsys.readouterr().out)
    assert printed["project"]["manifests"][0]["path"] == "sub/pyproject.toml"
    assert "root" not in printed["project"]


def test_print_config_keeps_a_root_that_is_not_the_working_directory(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pkg").mkdir()

    with pytest.raises(SystemExit):
        cli_utils.resolve_config(
            None, {"manifest": ("pyproject.toml",), "root": "pkg", "print_config": True}
        )

    printed = yaml.safe_load(capsys.readouterr().out)
    assert printed["project"]["root"] == str(tmp_path / "pkg")
    assert printed["project"]["manifests"][0]["path"] == "pyproject.toml"


def test_print_config_leaves_a_manifest_outside_the_root_absolute(capsys, tmp_path, monkeypatch):
    working_dir = tmp_path / "work"
    working_dir.mkdir()
    monkeypatch.chdir(working_dir)
    outside = tmp_path / "elsewhere" / "pyproject.toml"

    with pytest.raises(SystemExit):
        cli_utils.resolve_config(None, {"manifest": (str(outside),), "print_config": True})

    printed = yaml.safe_load(capsys.readouterr().out)
    assert printed["project"]["manifests"][0]["path"] == str(outside)
