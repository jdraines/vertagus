import pytest

from vertagus.errors import ConfigurationError
from vertagus.rules.comparison.library import (
    ComparisonRule,
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
def test_version_validators(validator: ComparisonRule,
                            versions: list[str],
                            expected: bool
                            ):
    vresult = validator.validate_comparison(versions)
    assert isinstance(vresult, bool)
    assert vresult == expected

def must_compare_more_than_one():
    with pytest.raises(ValueError):
        ManifestsComparisonRule({"manifests": []}).validate_comparison(["1.0.0"])

def test_validator_description():
    assert isinstance(Increasing({}).description, str) 
    assert isinstance(ManifestsComparisonRule({"manifests": []}).description, str)

def test_any_greater_than_none():
    assert Increasing({}).validate_comparison([None, "1.0.0"]) == True
    assert Increasing({}).validate_comparison(["", "1.0.0"]) == True

def test_manifests_comparison_requires_manifests_config():
    with pytest.raises(ConfigurationError, match="requires a `manifests` config"):
        ManifestsComparisonRule({})


def test_manifests_require_multiple_versions():
    with pytest.raises(ValueError):
        ManifestsComparisonRule({"manifests": []}).validate_comparison([])
    with pytest.raises(ValueError):
        ManifestsComparisonRule({"manifests": []}).validate_comparison(["1.0.0"])


def test_manifests_comparison_missing_manifest_names_are_reported():
    from unittest.mock import MagicMock
    from vertagus.core.project import Project

    def manifest(name, version):
        m = MagicMock()
        m.name = name
        m.version = version
        return m

    rule = ManifestsComparisonRule({"manifests": ["pyproject", "typo"]})
    project = Project(
        manifests=[manifest("pyproject", "1.0.0")],
        current_version_rules=[],
        version_increment_rules=[],
        manifest_versions_comparison_rules=[rule],
    )
    with pytest.raises(ConfigurationError, match=r"\['typo'\]"):
        project._run_manifest_versions_comparison_rules()


def test_manifests_comparison_requires_two_manifests():
    from unittest.mock import MagicMock
    from vertagus.core.project import Project

    m = MagicMock()
    m.name = "pyproject"
    m.version = "1.0.0"

    rule = ManifestsComparisonRule({"manifests": ["pyproject"]})
    project = Project(
        manifests=[m],
        current_version_rules=[],
        version_increment_rules=[],
        manifest_versions_comparison_rules=[rule],
    )
    with pytest.raises(ConfigurationError, match="at least two manifests"):
        project._run_manifest_versions_comparison_rules()
