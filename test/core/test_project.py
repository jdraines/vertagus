from copy import copy
import typing as T
from unittest.mock import patch, MagicMock

import pytest
from vertagus.core.project import (
    Project,
    ManifestBase,
    SingleVersionRule,
    VersionComparisonRule,
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
def mock_proj_alias():
    class MockProjAlias(AliasBase):
        
        def as_string(self, prefix: str = None) -> str:
            return f"{prefix}projtest-{self.tag_text}"
    return MockProjAlias


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


@pytest.fixture
def test_project(mock_manifests: list[ManifestBase],
                 mock_current_version_rules: list[T.Type[SingleVersionRule]],
                 mock_version_increment_rules: list[T.Type[VersionComparisonRule]],
                 mock_manifest_versions_comparison_rules: list[T.Type[VersionComparisonRule]],
                 mock_stage: Stage
                 ):
    return Project(
        manifests=mock_manifests,
        current_version_rules=mock_current_version_rules,
        version_increment_rules=mock_version_increment_rules,
        manifest_versions_comparison_rules=mock_manifest_versions_comparison_rules,
        stages=[mock_stage]
    )


def test_project_init(test_project):
    assert test_project is not None


def test_get_version(test_project):
    assert test_project.get_version() == "0.0.0"
    with patch("vertagus.core.project.Project._get_manifests", MagicMock()) as mock_get_manifests:
        mock_get_manifests.return_value = []
        with pytest.raises(ValueError):
            test_project.get_version()


def test_get_aliases(test_project, mock_stage_with_alias):
    test_project._stages = [mock_stage_with_alias]
    assert test_project.get_aliases("test_stage", "prefix-") == ["prefix-test-0.0.0"]


@patch("vertagus.core.project.Project._run_current_version_rules")
@patch("vertagus.core.project.Project._run_version_increment_rules")
@patch("vertagus.core.project.Project._run_manifest_versions_comparison_rules")
def test_validate_version(
    mock_run_manifest_versions_comparison_rules: MagicMock,
    mock_run_version_increment_rules: MagicMock,
    mock_run_current_version_rules: MagicMock,
    test_project: Project
):
    mock_run_current_version_rules.return_value = True
    mock_run_version_increment_rules.return_value = True
    mock_run_manifest_versions_comparison_rules.return_value = True
    assert test_project.validate_version("0.0.0", "test_stage")
    mock_run_current_version_rules.assert_called_once()
    mock_run_version_increment_rules.assert_called_once()
    mock_run_manifest_versions_comparison_rules.assert_called_once()

    mock_run_current_version_rules.return_value = False
    assert not test_project.validate_version("0.0.0", "test_stage")

    mock_run_current_version_rules.return_value = True
    mock_run_version_increment_rules.return_value = False
    assert not test_project.validate_version("0.0.0", "test_stage")

    mock_run_current_version_rules.return_value = True
    mock_run_version_increment_rules.return_value = True
    mock_run_manifest_versions_comparison_rules.return_value = False
    assert not test_project.validate_version("0.0.0", "test_stage")


@patch("vertagus.core.project.Project._get_current_version_rules")
def test_run_current_version_rules(
    mock_get_current_version_rules: MagicMock,
    test_project: Project,
    mock_current_version_rule_fail,
    mock_current_version_rule_pass
):
    mock_get_current_version_rules.return_value = [mock_current_version_rule_fail]
    assert not test_project._run_current_version_rules("0.0.0", "test_stage")
    mock_get_current_version_rules.assert_called_once()
    mock_get_current_version_rules.reset_mock()

    mock_get_current_version_rules.return_value = [mock_current_version_rule_pass]
    assert test_project._run_current_version_rules("0.0.0", "test_stage")
    mock_get_current_version_rules.assert_called_once()


@patch("vertagus.core.project.Project._get_version_increment_rules")
def test_run_version_increment_rules(
    mock_get_version_increment_rules: MagicMock,
    test_project: Project,
    mock_version_increment_rule_fail: VersionComparisonRule,
    mock_version_increment_rules: list[VersionComparisonRule]
):
    mock_get_version_increment_rules.return_value = [mock_version_increment_rule_fail]
    assert not test_project._run_version_increment_rules("0.0.0", "0.0.1", "test_stage")
    mock_get_version_increment_rules.assert_called_once()
    mock_get_version_increment_rules.reset_mock()

    mock_get_version_increment_rules.return_value = mock_version_increment_rules
    assert test_project._run_version_increment_rules("0.0.0", "0.0.1", "test_stage")
    mock_get_version_increment_rules.assert_called_once()


@patch("vertagus.core.project.Project._get_manifest_versions_comparison_rules")
def test_run_manifest_versions_comparison_rules(
    mock_get_manifest_versions_comparison_rules: MagicMock,
    test_project: Project,
    mock_manifest_versions_comparison_rule_fail: ManifestsComparisonRule,
    mock_manifest_versions_comparison_rules: list[ManifestsComparisonRule]
):
    mock_get_manifest_versions_comparison_rules.return_value = [mock_manifest_versions_comparison_rule_fail]
    assert not test_project._run_manifest_versions_comparison_rules("test_stage")
    mock_get_manifest_versions_comparison_rules.assert_called_once()
    mock_get_manifest_versions_comparison_rules.reset_mock()

    mock_get_manifest_versions_comparison_rules.return_value = mock_manifest_versions_comparison_rules
    assert test_project._run_manifest_versions_comparison_rules("test_stage")
    mock_get_manifest_versions_comparison_rules.assert_called_once()


def test_stages_property(test_project: Project,
                         mock_stage: Stage):
    assert test_project.stages == [mock_stage]


def test__get_current_version_rules(test_project: Project,
                                    mock_current_version_rules: list[SingleVersionRule],
                                    mock_current_version_rule_fail: SingleVersionRule
                                    ):
    assert test_project._get_current_version_rules() == mock_current_version_rules
    assert test_project._get_current_version_rules("test_stage") == mock_current_version_rules
    test_project._stages[0]._current_version_rules = mock_current_version_rules + [mock_current_version_rule_fail]
    assert test_project._get_current_version_rules("test_stage") == mock_current_version_rules + [mock_current_version_rule_fail]


def test__get_version_increment_rules(test_project: Project,
                                     mock_version_increment_rules: list[VersionComparisonRule],
                                     mock_version_increment_rule_fail: VersionComparisonRule
                                     ):
    assert test_project._get_version_increment_rules() == mock_version_increment_rules
    assert test_project._get_version_increment_rules("test_stage") == mock_version_increment_rules
    test_project._stages[0]._version_increment_rules = mock_version_increment_rules + [mock_version_increment_rule_fail]
    assert test_project._get_version_increment_rules("test_stage") == mock_version_increment_rules + [mock_version_increment_rule_fail]


def test__get_manifest_versions_comparison_rules(test_project: Project,
                                                mock_manifest_versions_comparison_rules: list[ManifestsComparisonRule],
                                                mock_manifest_versions_comparison_rule_fail: ManifestsComparisonRule
                                                ):
    assert test_project._get_manifest_versions_comparison_rules() == mock_manifest_versions_comparison_rules
    assert test_project._get_manifest_versions_comparison_rules("test_stage") == mock_manifest_versions_comparison_rules
    test_project._stages[0]._manifest_versions_comparison_rules = mock_manifest_versions_comparison_rules + [mock_manifest_versions_comparison_rule_fail]
    assert test_project._get_manifest_versions_comparison_rules("test_stage") == mock_manifest_versions_comparison_rules + [mock_manifest_versions_comparison_rule_fail]


def test__get_manifests(test_project: Project,
                        mock_stage: Stage,
                        mock_manifests: list[ManifestBase],
                        mock_manifest_higher_version: ManifestBase
                        ):
    assert mock_manifest_higher_version.version == "0.0.1"
    assert test_project._get_manifests() == mock_manifests
    assert test_project._get_manifests("test_stage") == mock_manifests
    test_project._stages = [copy(mock_stage)]
    test_project._stages[0]._manifests = [mock_manifest_higher_version]
    assert len(test_project._get_manifests("test_stage")) == 2
    assert test_project._get_manifests("test_stage")[1] == mock_manifest_higher_version


def test__get_version_aliases(test_project: Project,
                              mock_alias
                              ):
    test_project.aliases = [mock_alias]
    aliases = test_project._get_version_aliases("0.0.0")
    assert [a.as_string("prefix-") for a in aliases] == ["prefix-test-0.0.0"]


def test_get_aliases(test_project: Project,
                     mock_proj_alias,
                     mock_stage_with_alias: Stage
                     ):
    test_project._stages = [mock_stage_with_alias]
    test_project.aliases = [mock_proj_alias]
    aliases = test_project.get_aliases("test_stage") 
    alias_strs = [alias.as_string("prefix-") for alias in aliases]
    assert alias_strs == ["prefix-projtest-0.0.0", "prefix-test-0.0.0"]


def test_bump_version(test_project: Project):
    test_project = copy(test_project)
    test_project.bumper = MagicMock()
    test_project.bumper.bump = MagicMock(return_value="1.1.0")
    manifest = MagicMock()
    test_project.get_version = MagicMock(return_value="1.0.0")
    test_project._get_manifests = MagicMock(return_value=[manifest])
    new_version = test_project.bump_version("test_stage", "foo")
    test_project.bumper.bump.assert_called_once_with(
        "1.0.0", "foo"
    )
    manifest.update_version.assert_called_once_with(
        "1.1.0"
    )
    assert new_version == "1.1.0"
