import typing as T

import pytest
from unittest.mock import patch, MagicMock
from vertagus.core import stage
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.core.stage import (
    ManifestBase,
    ManifestsComparisonRule,
    Stage
)
from vertagus.core.tag_base import AliasBase


@pytest.fixture
def mock_manifests():
    manifest = ManifestBase(
        name="mock_manifest",
        path="mock_manifest_path",
        loc=["mock_manifest_loc"]
    )
    manifest.version = "0.0.0"
    return [manifest]


@pytest.fixture
def mock_manifest_higher_version():
    manifest = ManifestBase(
        name="mock_manifest_higher_version",
        path="mock_manifest_path",
        loc=["mock_manifest_loc"]
    )
    manifest.version = "0.0.1"
    return manifest

@pytest.fixture
def mock_current_version_rule_pass():
    class MockCurrentVersionRulePass(SingleVersionRule):
        name = "mock_current_version_rule"
        @classmethod
        def validate_version(cls, version: str):
            return True
    return MockCurrentVersionRulePass


@pytest.fixture
def mock_current_version_rules(
    mock_current_version_rule_pass
):
    return [mock_current_version_rule_pass]


@pytest.fixture
def mock_current_version_rule_fail():
    class MockCurrentVersionRuleFail(SingleVersionRule):
        name = "mock_current_version_rule_fail"
        @classmethod
        def validate_version(cls, version: str):
            return False
    return MockCurrentVersionRuleFail


@pytest.fixture
def mock_version_increment_rules():
    class MockVersionIncrementRule(VersionComparisonRule):
        name = "mock_version_increment_rule"
        def validate_comparison(self, versions: T.Sequence[str]):
            return True
    return [MockVersionIncrementRule({})]


@pytest.fixture
def mock_version_increment_rule_fail():
    class MockVersionIncrementRule(VersionComparisonRule):
        name = "mock_version_increment_rule_fail"
        def validate_comparison(self, versions: T.Sequence[str]):
            return False
    return MockVersionIncrementRule({})


@pytest.fixture
def mock_manifest_versions_comparison_rules():
    class MockManifetVersionsComparisonRule(ManifestsComparisonRule):
        name = "mock_version_increment_rule"
        def validate_comparison(self, versions: T.Sequence[str]):
            return True
        
    config = {"manifests": ["mock_manifest"]}
    return [MockManifetVersionsComparisonRule(config)]


@pytest.fixture
def mock_manifest_versions_comparison_rule_fail():
    class MockManifetVersionsComparisonRuleFail(ManifestsComparisonRule):
        name = "mock_version_increment_rule_fail"
        def validate_comparison(self, versions: T.Sequence[str]):
            return False
        
    config = {"manifests": ["mock_manifest"]}
    return MockManifetVersionsComparisonRuleFail(config)


@pytest.fixture
def mock_alias():
    class MockAlias(AliasBase):
        def as_string(self, prefix: str = None) -> str:
            return f"{prefix}test-{self.tag_text}"
    return MockAlias



@pytest.fixture
def mock_stage(mock_manifests,
               mock_current_version_rules,
               mock_version_increment_rules,
               mock_manifest_versions_comparison_rules
               ):
    return Stage(
        name='test_stage',
        manifests=mock_manifests,
        current_version_rules=mock_current_version_rules,
        version_increment_rules=mock_version_increment_rules,
        manifest_versions_comparison_rules=mock_manifest_versions_comparison_rules
    )


@pytest.fixture
def mock_stage_with_alias(mock_manifests,
               mock_current_version_rules,
               mock_version_increment_rules,
               mock_manifest_versions_comparison_rules,
               mock_alias
               ):
    return Stage(
        name='test_stage',
        manifests=mock_manifests,
        current_version_rules=mock_current_version_rules,
        version_increment_rules=mock_version_increment_rules,
        manifest_versions_comparison_rules=mock_manifest_versions_comparison_rules,
        aliases=[mock_alias]
    )


def test_stage_init(mock_stage: Stage,
                    mock_manifests: list[ManifestBase],
                    mock_current_version_rules: list[T.Type[SingleVersionRule]],
                    mock_version_increment_rules: list[VersionComparisonRule],
                    mock_manifest_versions_comparison_rules: list[ManifestsComparisonRule]
                    ):
    assert mock_stage.name == 'test_stage'
    assert mock_stage.manifests == mock_manifests
    assert mock_stage.current_version_rules == mock_current_version_rules
    assert mock_stage.version_increment_rules == mock_version_increment_rules
    assert mock_stage.manifest_versions_comparison_rules == mock_manifest_versions_comparison_rules


def test_stage_get_version_aliases(mock_stage_with_alias: Stage):
    aliases = mock_stage_with_alias.get_version_aliases("0.0.0")
    assert [a.as_string("prefix-") for a in aliases] == ["prefix-test-0.0.0"]
