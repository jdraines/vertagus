import pytest
from unittest.mock import MagicMock, patch

from vertagus.aliases import loader as a_loader


@patch('vertagus.aliases.loader.library')
def test_load_aliases(library: MagicMock):

    class MockAliasNoSubclass:
        name = "mock_alias_no_subclass"

    class MockAliasYesSubclass(a_loader.AliasBase):
        name = "mock_alias_yes_subclass"
    
    library.MockAliasNoSubclass = MockAliasNoSubclass
    library.MockAliasYesSubclass = MockAliasYesSubclass

    aliases = a_loader.load_aliases()
    assert len(aliases) == 1
    assert aliases[0] == MockAliasYesSubclass

    library.MockAliasYesSubclass = None
    library.AliasBase = None

    aliases = a_loader.load_aliases()
    assert not aliases


@patch('vertagus.aliases.loader.load_aliases')
def test_get_aliases(load_aliases: MagicMock):

    class MockAlias(a_loader.AliasBase):
        name = "mock_alias"
    
    load_aliases.return_value = [MockAlias]

    aliases = a_loader.get_aliases()
    assert len(aliases) == 0

    aliases = a_loader.get_aliases(["mock_alias"])
    assert len(aliases) == 1
    assert aliases[0] == MockAlias

    with pytest.raises(ValueError):
        a_loader.get_aliases(["mock_alias", "not_an_alias"])
