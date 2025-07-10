from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from vertagus.cli import utils as cli_utils


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
    mock_validate_config_path.return_value = "/my/config/path.yaml"
    mock_load_config.return_value = {"project": {"root": "/mock/root"}}

    config = cli_utils.load_config(None)    
    mock_validate_config_path.assert_called_once_with(None)
    mock_load_config.assert_called_once_with("/my/config/path.yaml")
    assert config == {"project": {"root": str(Path("/mock/root"))}}

    mock_load_config.return_value = {"project": {}}
    config = cli_utils.load_config(None)
    assert config == {"project": {"root": str(Path("/my/config"))}}
