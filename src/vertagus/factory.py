from dataclasses import asdict
import os.path

from vertagus.core.project import Project
from vertagus.core.stage import Stage
from vertagus.core.tag_base import AliasBase
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.core.scm_base import ScmBase

from vertagus.providers.scm.registry import get_scm_cls
from vertagus.providers.manifest.registry import get_manifest_cls
from vertagus.aliases.loader import get_aliases
from vertagus.rules.single_version.loader import get_rules as get_single_version_rules
from vertagus.rules.comparison.loader import get_rules as get_version_comparison_rules

from .configuration import types as t


def create_project(data: t.ProjectData, root:str = None) -> Project:
    return Project(
        manifests=create_manifests(data.manifests, root),
        current_version_rules=create_single_version_rules(data.rules.current),
        version_increment_rules=create_version_comparison_rules(data.rules.increment, {}),
        manifest_versions_comparison_rules=create_version_comparison_rules(
            ["manifests_comparison"],
            {"manifests": data.rules.manifest_comparisons}
        ),
        stages=create_stages(data.stages),
        aliases=create_aliases(data.aliases)
    )


def create_manifests(manifest_data: list[t.ManifestData], root: str = None) -> list[ManifestBase]:
    manifests = []
    for each in manifest_data:
        if root:
            each.path = os.path.join(root, each.path)
        manifest_cls = get_manifest_cls(each.type)
        manifests.append(manifest_cls(**each.config()))
    return manifests


def create_single_version_rules(rule_names: list[str]) -> list[SingleVersionRule]:
    return get_single_version_rules(rule_names)


def create_version_comparison_rules(rule_names: list[str], config) -> list[VersionComparisonRule]:
    rule_classes = get_version_comparison_rules(rule_names)
    return [rule_cls(config=config) for rule_cls in rule_classes]

def create_aliases(alias_names: list[str]) -> list[AliasBase]:
    return get_aliases(alias_names)

def create_stages(stage_data: dict[str, t.StageData]) -> list[Stage]:
    stages = []
    for data in stage_data:
        stages.append(Stage(
            name=data.name,
            manifests=create_manifests(data.manifests),
            current_version_rules=create_single_version_rules(data.rules.current),
            version_increment_rules=create_version_comparison_rules(data.rules.increment, {}),
            manifest_versions_comparison_rules=create_version_comparison_rules(
                ["manifests_comparison"],
                {"manifests": data.rules.manifest_comparisons}
            ),
            aliases=create_aliases(data.aliases),
        ))
    return stages


def create_scm(root: str, data: t.ScmData) -> ScmBase:
    scm_cls = get_scm_cls(data.scm_type)
    return scm_cls(root, **data.config())
