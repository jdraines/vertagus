import pytest
from vertagus.rules.single_version.library import (
    SingleVersionRule,
    NotEmpty, RegexMmp, RegexDevMmp, RegexBetaMmp, RegexRcMmp, RegexAlphaMmp,
    RegexMm, RegexDevMm, RegexBetaMm, RegexRcMm, RegexAlphaMm,
    CustomRegexRule
)
from vertagus.utils import regex as regex_utils


@pytest.mark.parametrize("validator, version, expected", [
    (NotEmpty, "", False),
    (NotEmpty, "1.0.0", True),
    (RegexMmp, "1.0.0", True),
    (RegexMmp, "1.0", False),
    (RegexDevMmp, "1.0.0dev1", True),
    (RegexDevMmp, "1.0.0-dev1", True),
    (RegexDevMmp, "1.0.0a1", False),
    (RegexBetaMmp, "1.0.0b1", True),
    (RegexBetaMmp, "1.0.0-b1", True),
    (RegexBetaMmp, "1.0.0", False),
    (RegexRcMmp, "1.0.0rc1", True),
    (RegexRcMmp, "1.0.0-rc1", True),
    (RegexRcMmp, "1.0.0", False),
    (RegexAlphaMmp, "1.0.0a1", True),
    (RegexAlphaMmp, "1.0.0", False),
    (RegexMm, "1.0", True),
    (RegexMm, "1.0.0", False),
    (RegexDevMm, "1.0dev1", True),
    (RegexDevMm, "1.0-dev1", True),
    (RegexDevMm, "1.0", False),
    (RegexBetaMm, "1.0b1", True),
    (RegexBetaMm, "1.0-b1", True),
    (RegexBetaMm, "1.0", False),
    (RegexRcMm, "1.0rc1", True),
    (RegexRcMm, "1.0-rc1", True),
    (RegexRcMm, "1.0", False),
    (RegexAlphaMm, "1.0a1", True),
    (RegexAlphaMm, "1.0-a1", True),
    (RegexAlphaMm, "1.0", False),
])
def test_version_validators(validator: SingleVersionRule,
                            version: str,
                            expected: bool
                            ):
    vresult = validator.validate_version(version)
    assert isinstance(vresult, bool)
    assert validator.validate_version(version) == expected


def test_validator_description():
    assert RegexMmp().description == f"Version must match the pattern: {regex_utils.patterns['mmp']}"
    assert NotEmpty().description == "Version must not be empty."

@pytest.mark.parametrize(
    ["pattern", "version", "expected"], [
    (r"^\d+\.\d+\.\d+$", "1.0.0", True),
    (r"^\d+\.\d+\.\d+$", "1.0", False),
    (r"^\d+\.\d+\.\d+-dev\.\d+$", "1.0.0-dev.1", True),
    (r"^\d+\.\d+\.\d+-dev\.\d+$", "1.0.0", False),
])
def test_custom_regex_rule(pattern: str, version: str, expected: bool):
    rule = CustomRegexRule({"pattern": pattern})
    assert rule.validate_version(version) == expected
