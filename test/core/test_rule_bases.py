import pytest

from vertagus.core import rule_bases as rb


def test_version_comparison_rule_init():
    config = {"key": "value"}
    rule = rb.VersionComparisonRule(config=config)
    assert rule.config == config


def test_version_comparison_rule_hash():
    config1 = {"key": "value"}
    config2 = {"key": "value2"}
    rule1 = rb.VersionComparisonRule(config=config1)
    rule2 = rb.VersionComparisonRule(config=config2)
    rule3 = rb.VersionComparisonRule(config=config1)
    assert hash(rule1) != hash(rule2)
    assert hash(rule1) == hash(rule3)


def test_version_comparison_rule_validate_comparison_is_virtual():
    rule = rb.VersionComparisonRule(config={})
    with pytest.raises(NotImplementedError):
        rule.validate_comparison(versions=["1.0.0", "1.0.1"])


def test_single_version_rule_validate_version_is_virtual():
    with pytest.raises(NotImplementedError):
        rb.SingleVersionRule.validate_version(version="1.0.0")

