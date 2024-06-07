import pytest
from unittest.mock import MagicMock, patch

from vertagus.rules.comparison import loader as comp_loader


@patch('vertagus.rules.comparison.loader.library')
def test_load_rules(library: MagicMock):

    class MockRuleNoSubclass:
        name = "mock_rule_no_subclass"

    class MockRuleYesSubclass(comp_loader.VersionComparisonRule):
        name = "mock_rule_yes_subclass"
    
    library.MockRuleNoSubclass = MockRuleNoSubclass
    library.MockRuleYesSubclass = MockRuleYesSubclass

    rules = comp_loader.load_rules()
    assert len(rules) == 1
    assert rules[0] == MockRuleYesSubclass

    library.MockRuleYesSubclass = None
    library.VersionComparisonRule = None

    rules = comp_loader.load_rules()
    assert not rules


@patch('vertagus.rules.comparison.loader.load_rules')
def test_get_rules(load_rules: MagicMock):

    class MockRule(comp_loader.VersionComparisonRule):
        name = "mock_rule"
    
    load_rules.return_value = [MockRule]

    rules = comp_loader.get_rules()
    assert len(rules) == 1
    assert rules[0] == MockRule

    rules = comp_loader.get_rules(["mock_rule"])
    assert len(rules) == 1
    assert rules[0] == MockRule

    with pytest.raises(ValueError):
        comp_loader.get_rules(["mock_rule", "not_a_rule"])
