import pytest
import typing as T
from vertagus.core import package_base as pb
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.rules.comparison.library import ManifestsComparisonRule


@pytest.fixture
def mock_manifests():
    return [ManifestBase(
        name="mock_manifest",
        path="mock_manifest_path",
        loc=["mock_manifest_loc"]
    )]


@pytest.fixture
def mock_current_version_rules():
    class MockCurrentVersionRule(SingleVersionRule):
        name = "mock_current_version_rule"
        @classmethod
        def validate_version(cls, version: str):
            return True
    return [MockCurrentVersionRule]


@pytest.fixture
def mock_version_increment_rules():
    class MockVersionIncrementRule(VersionComparisonRule):
        name = "mock_version_increment_rule"
        def validate_comparison(self, versions: T.Sequence[str]):
            return True
    return [MockVersionIncrementRule({})]


@pytest.fixture
def mock_manifest_versions_comparison_rules():
    class MockManifetVersionsComparisonRule(ManifestsComparisonRule):
        name = "mock_version_increment_rule"
        def validate_comparison(self, versions: T.Sequence[str]):
            return True
        
    config = {"manifests": ["test_manifest"]}
    return [MockManifetVersionsComparisonRule(config)]


@pytest.fixture
def package(mock_manifests: list[ManifestBase],
            mock_current_version_rules: list[T.Type[SingleVersionRule]],
            mock_version_increment_rules: list[T.Type[VersionComparisonRule]],
            mock_manifest_versions_comparison_rules: list[T.Type[VersionComparisonRule]],
            ):
    return pb.Package(
        mock_manifests,
        mock_current_version_rules,
        mock_version_increment_rules,
        mock_manifest_versions_comparison_rules
    )


def test_init_package(package: pb.Package,
                      mock_manifests: list[ManifestBase],
                      mock_current_version_rules: list[T.Type[SingleVersionRule]],
                      mock_version_increment_rules: list[T.Type[VersionComparisonRule]],
                      mock_manifest_versions_comparison_rules: list[T.Type[VersionComparisonRule]]
                      ):
    assert package._manifests == mock_manifests
    assert package._current_version_rules == mock_current_version_rules
    assert package._version_increment_rules == mock_version_increment_rules
    assert package._manifest_versions_comparison_rules == mock_manifest_versions_comparison_rules
