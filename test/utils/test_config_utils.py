import pytest
from unittest.mock import MagicMock, patch

import yaml
import tomli
from vertagus.utils import config as cfgutils

@patch('vertagus.utils.config.yaml.safe_load')
def test_is_yaml(safe_load: MagicMock):

    def mock_safe_load_with_raise(doc):
        raise yaml.YAMLError()
    
    doc = "key: value"
    cfgutils.is_yaml(doc)
    safe_load.assert_called_once_with(doc)

    safe_load.reset_mock()
    safe_load.side_effect = mock_safe_load_with_raise
    assert not cfgutils.is_yaml(doc)

    with pytest.raises(yaml.YAMLError):
        cfgutils.is_yaml(doc, "file.yaml")


@patch('vertagus.utils.config.tomli.loads')
def test_is_toml(loads: MagicMock):

    def mock_loads_with_raise(doc):
        raise tomli.TOMLDecodeError()
    
    doc = "key = value"
    cfgutils.is_toml(doc, "file.toml")
    loads.assert_called_once_with(doc)

    loads.reset_mock()
    loads.side_effect = mock_loads_with_raise
    assert not cfgutils.is_toml(doc)

    with pytest.raises(tomli.TOMLDecodeError):
        cfgutils.is_toml(doc, "file.toml")
    