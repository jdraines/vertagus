import pytest
from vertagus.rules.comparison.library import (
    VersionComparisonRule,
    Increasing,
    ManifestsComparisonRule
)
from vertagus.utils import regex as regex_utils


@pytest.mark.parametrize("validator, versions, expected", [
    (Increasing({}), ("1.0.1", "1.0.1"), False),
    (Increasing({}), ("1.0.1", "1.0.2"), True),
    (Increasing({}), ("1.0.1", "1.1.0"), True),
    (Increasing({}), ("1.0.1", "2.0.0"), True),
    (ManifestsComparisonRule({"manifests": []}), ["1.0.0", "1.0.0"], True),
    (ManifestsComparisonRule({"manifests": []}), ["1.0.0", "1.0.0", "1.0.0"], True),
    (ManifestsComparisonRule({"manifests": []}), ["1.0.0", "1.0.0", "1.0.1"], False),
])
def test_version_validators(validator: VersionComparisonRule,
                            versions: list[str],
                            expected: bool
                            ):
    vresult = validator.validate_comparison(versions)
    assert isinstance(vresult, bool)
    assert vresult == expected

def must_compare_more_than_one():
    with pytest.raises(ValueError):
        ManifestsComparisonRule({"manifests": []}).validate_comparison(["1.0.0"])
