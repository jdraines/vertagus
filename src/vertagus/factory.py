from dataclasses import asdict

from vertagus.core.project import Project
from vertagus.core.stage import Stage
from vertagus.core.alias_base import AliasBase
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.core.scm_base import ScmBase

from vertagus.providers.scm.registry import get_scm_cls
from vertagus.providers.manifest.registry import get_manifest_cls
from vertagus.aliases.loader import get_aliases
from vertagus.rules.single_version.loader import get_rules as get_single_version_rules
from vertagus.rules.comparison.loader import get_rules as get_version_comparison_rules

from .configuration import _types as _T


def create_project(data: _T.ProjectData) -> Project:
    return Project(
        manifests=create_manifests(data.manifests),
        current_version_rules=create_single_version_rules(data.rules.current),
        version_increment_rules=create_version_comparison_rules(data.rules.increment),
        manifest_versions_comparison_rules=create_version_comparison_rules(data.rules.manifest_comparisons),
        stages=create_stages(data.stages),
    )


def create_manifests(manifest_data: list[_T.ManifestData]) -> list[ManifestBase]:
    manifests = []
    for each in manifest_data:
        manifest_cls = get_manifest_cls(each.type)
        manifests.append(manifest_cls(**each.config()))
    return manifests


def create_single_version_rules(rule_names: list[str]) -> list[SingleVersionRule]:
    return [get_single_version_rules(name) for name in rule_names]


def create_version_comparison_rules(rule_names: list[str]) -> list[VersionComparisonRule]:
    return [get_version_comparison_rules(name) for name in rule_names]


def create_aliases(alias_names: list[str]) -> list[AliasBase]:
    return [get_aliases(name) for name in alias_names]


def create_stages(stage_data: dict[str, _T.StageData]) -> list[Stage]:
    stages = []
    for name, data in stage_data.items():
        stages.append(Stage(
            name=name,
            manifests=create_manifests(data.manifests),
            current_version_rules=create_single_version_rules(data.rules.current),
            version_increment_rules=create_version_comparison_rules(data.rules.increment),
            manifest_versions_comparison_rules=create_version_comparison_rules(data.rules.manifest_comparisons),
            aliases=create_aliases(data.aliases),
        ))
    return stages


def create_scm(data: _T.ScmData) -> ScmBase:
    scm_cls = get_scm_cls(data.scm_type)
    return scm_cls(**data.config())
