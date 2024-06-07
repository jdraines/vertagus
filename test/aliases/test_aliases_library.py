import pytest
from vertagus.aliases.library import (
    StringAlias,
    StableAlias,
    LatestAlias,
    StablePrefixedAlias,
    LatestPrefixedAlias,
    MajorMinor,
    AliasBase
)
from vertagus.utils import regex as regex_utils


@pytest.fixture
def prefix():
    return "v"


@pytest.mark.parametrize("alias_cls, version, expected, expected_w_prefix", [
    (StableAlias, "1.0.0", "stable", "stable"),
    (LatestAlias, "1.0.0", "latest", "latest"),
    (StablePrefixedAlias, "1.0.0", "stable", "vstable"),
    (LatestPrefixedAlias, "1.0.0", "latest", "vlatest"),
    (MajorMinor, "1.0.0", "1.0", "v1.0"),
    (MajorMinor, "1.0", "1.0", "v1.0")
])
def test_version_validators(alias_cls: type[AliasBase],
                            version: str,
                            expected: bool,
                            expected_w_prefix: str,
                            prefix: str
                            ):
    alias = alias_cls(version)
    assert alias.as_string() == expected
    assert alias.as_string(prefix) == expected_w_prefix


def test_major_minor_must_have_two_parts():
    with pytest.raises(ValueError):
        MajorMinor("1").as_string()
