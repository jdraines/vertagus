import pytest
from unittest.mock import MagicMock, patch

from vertagus.rules.single_version import loader as sv_loader


@patch('vertagus.rules.single_version.loader.library')
def test_load_rules(library: MagicMock):

    class MockRuleNoSubclass:
        name = "mock_rule_no_subclass"

    class MockRuleYesSubclass(sv_loader.SingleVersionRule):
        name = "mock_rule_yes_subclass"
    
    library.MockRuleNoSubclass = MockRuleNoSubclass
    library.MockRuleYesSubclass = MockRuleYesSubclass

    rules = sv_loader.load_rules()
    assert len(rules) == 1
    assert rules[0] == MockRuleYesSubclass

    library.MockRuleYesSubclass = None
    library.SingleVersionRule = None

    rules = sv_loader.load_rules()
    assert not rules


@patch('vertagus.rules.single_version.loader.load_rules')
def test_get_rules(load_rules: MagicMock):

    class MockRule(sv_loader.SingleVersionRule):
        name = "mock_rule"
    
    load_rules.return_value = [MockRule]

    rules = sv_loader.get_rules()
    assert len(rules) == 1
    assert rules[0] == MockRule

    rules = sv_loader.get_rules(["mock_rule"])
    assert len(rules) == 1
    assert rules[0] == MockRule

    with pytest.raises(ValueError):
        sv_loader.get_rules(["mock_rule", "not_a_rule"])
