from dataclasses import asdict

from vertagus.core.project import Project
from vertagus.core.stage import Stage
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import ValidationRule, ComparisonRule

from vertagus.providers.manifest.registry import get_manifest_cls
from vertagus.rules.validations.loader import get_rules as get_validation_rules
from vertagus.rules.comparisons.loader import get_rules as get_comparison_rules

from . import _types as _T


def create_project(data: _T.ProjectData) -> Project:
    return Project(
        manifests=create_manifests(data.manifests),
        validation_rules=create_validation_rules(data.rules.validations),
        comparison_rules=create_comparison_rules(data.rules.comparisons),
        stages=create_stages(data.stages),
    )


def create_manifests(manifest_data: list[_T.ManifestData]) -> list[ManifestBase]:
    manifests = []
    for each in manifest_data:
        manifest_cls = get_manifest_cls(each.type)
        manifests.append(manifest_cls(**each.config()))
    return manifests


def create_validation_rules(rule_names: list[str]) -> list[ValidationRule]:
    return [get_validation_rules(name) for name in rule_names]


def create_comparison_rules(rule_names: list[str]) -> list[ComparisonRule]:
    return [get_comparison_rules(name) for name in rule_names]


def create_stages(stage_data: dict[str, _T.StageData]) -> list[Stage]:
    stages = []
    for name, data in stage_data.items():
        stages.append(Stage(
            name=name,
            manifests=create_manifests(data.manifests),
            validation_rules=create_validation_rules(data.rules.validations),
            comparison_rules=create_comparison_rules(data.rules.comparisons),
        ))
    return stages
