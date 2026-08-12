import os.path

from vertagus.aliases.loader import get_aliases
from vertagus.bumpers.registry import BumperBase, get_bumper_cls
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.project import Project
from vertagus.core.rule_bases import ComparisonRule, SingleVersionRule
from vertagus.core.scm_base import ScmBase
from vertagus.core.stage import Stage
from vertagus.core.tag_base import AliasBase
from vertagus.errors import ConfigurationError
from vertagus.providers.manifest.registry import get_manifest_cls
from vertagus.providers.scm.registry import get_scm_cls
from vertagus.rules.comparison.library import ManifestsComparisonRule
from vertagus.rules.registry import get_rule

from .configuration import types as t


def create_rules(
    rule_items: list[str | dict],
) -> tuple[list[SingleVersionRule], list[ComparisonRule], list[ManifestsComparisonRule]]:
    """Parse a flat list of rule items and return categorized rule instances."""
    single_version_rules: list[SingleVersionRule] = []
    comparison_rules: list[ComparisonRule] = []
    manifest_comparison_rules: list[ManifestsComparisonRule] = []

    for item in rule_items:
        if isinstance(item, str):
            rule_name = item
            config = {}
        elif isinstance(item, dict):
            rule_name = item["type"]
            config = item.get("config", {})
        else:
            raise ConfigurationError(
                f"Invalid rule item: {item!r}. Each rule must be either a rule name, or a "
                "mapping with a `type` key and an optional `config` key."
            )

        rule_cls = get_rule(rule_name)
        rule_instance = rule_cls(config=config)

        if isinstance(rule_instance, ManifestsComparisonRule):
            manifest_comparison_rules.append(rule_instance)
        elif isinstance(rule_instance, ComparisonRule):
            comparison_rules.append(rule_instance)
        elif isinstance(rule_instance, SingleVersionRule):
            single_version_rules.append(rule_instance)
        else:
            raise ConfigurationError(f"Unknown rule type: {rule_cls}")

    return single_version_rules, comparison_rules, manifest_comparison_rules


def create_project(data: t.ProjectData) -> Project:
    sv_rules, comp_rules, manifest_rules = create_rules(data.rules.rules)
    return Project(
        manifests=create_manifests(data.manifests, data.root),
        current_version_rules=sv_rules,
        version_increment_rules=comp_rules,
        manifest_versions_comparison_rules=manifest_rules,
        stages=create_stages(data.stages, data.root) if data.stages else None,
        aliases=create_aliases(data.aliases or []),
        bumper=create_bumper(data.bumper) if data.bumper else None,
    )


def create_manifests(manifest_data: list[t.ManifestData], root: str | None = None) -> list[ManifestBase]:
    manifests = []
    for each in manifest_data:
        if root:
            each.path = os.path.join(root, each.path)
        manifest_cls = get_manifest_cls(each.type)
        manifests.append(manifest_cls(**each.config()))
    return manifests


def create_aliases(alias_names: list[str]) -> list[type[AliasBase]]:
    return get_aliases(alias_names)


def create_stages(stage_data: list[t.StageData], project_root: str | None = None) -> list[Stage]:
    stages = []
    for data in stage_data:
        sv_rules, comp_rules, manifest_rules = create_rules(data.rules.rules)
        stages.append(
            Stage(
                name=data.name,
                manifests=create_manifests(data.manifests, project_root),
                current_version_rules=sv_rules,
                version_increment_rules=comp_rules,
                manifest_versions_comparison_rules=manifest_rules,
                aliases=create_aliases(data.aliases or []),
                bumper=create_bumper(data.bumper) if data.bumper else None,
            )
        )
    return stages


def create_scm(data: t.ScmData) -> ScmBase:
    scm_cls = get_scm_cls(data.scm_type)
    return scm_cls(**data.config())


def create_bumper(data: t.BumperData) -> BumperBase:
    """
    Create a bumper instance based on the provided data.
    """
    bumper_cls = get_bumper_cls(data.type)
    return bumper_cls(**data.kwargs())
