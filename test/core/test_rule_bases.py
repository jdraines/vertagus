import pytest

from vertagus.core import rule_bases as rb


def test_rule_init_default_config():
    rule = rb.Rule()
    assert rule.config == {}


def test_rule_init_with_config():
    config = {"key": "value"}
    rule = rb.Rule(config=config)
    assert rule.config == config


def test_comparison_rule_hash():
    config1 = {"key": "value"}
    config2 = {"key": "value2"}
    rule1 = rb.ComparisonRule(config=config1)
    rule2 = rb.ComparisonRule(config=config2)
    rule3 = rb.ComparisonRule(config=config1)
    assert hash(rule1) != hash(rule2)
    assert hash(rule1) == hash(rule3)


def test_rule_equality_by_class_and_config():
    assert rb.Rule(config={"key": "value"}) == rb.Rule(config={"key": "value"})
    assert rb.Rule(config={"key": "value"}) != rb.Rule(config={"key": "other"})
    assert rb.SingleVersionRule() != rb.ComparisonRule()


def test_distinct_equal_rule_instances_dedupe():
    rules = [rb.SingleVersionRule(), rb.SingleVersionRule()]
    assert list(dict.fromkeys(rules)) == [rules[0]]


def test_comparison_rule_validate_comparison_is_virtual():
    rule = rb.ComparisonRule(config={})
    with pytest.raises(NotImplementedError):
        rule.validate_comparison(versions=["1.0.0", "1.0.1"])


def test_single_version_rule_validate_version_is_virtual():
    rule = rb.SingleVersionRule()
    with pytest.raises(NotImplementedError):
        rule.validate_version(version="1.0.0")
