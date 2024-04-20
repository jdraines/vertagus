import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.rules.comparison.library import ManifestsComparisonRule
from .package_base import Package
from .stage import Stage

class Project(Package):
    
    def __init__(self,
                 manifests: list[ManifestBase],
                 current_version_rules: list[T.Type[SingleVersionRule]],
                 version_increment_rules: list[VersionComparisonRule],
                 manifest_versions_comparison_rules: list[ManifestsComparisonRule],
                 stages: list[Stage] = None
                 ):
        super().__init__(
            manifests=manifests,
            current_version_rules=current_version_rules,
            version_increment_rules=version_increment_rules,
            manifest_versions_comparison_rules=manifest_versions_comparison_rules,
        )
        self._stages = stages or []

    @property
    def stages(self):
        return self._stages
    
    def get_version(self, stage_name: str = None):
        manifests = self._get_manifests(stage_name)
        if not manifests:
            raise ValueError("No manifests found.")
        return manifests[0].version

    def get_aliases(self, stage_name: str, alias_prefix: str = None) -> list[str]:
        version = self.get_version()
        stage = self._get_stage(stage_name)
        return stage.get_version_aliases(version, alias_prefix)

    def validate_version(self, previous_version: str, stage_name: str = None):
        current_version = self.get_version(stage_name)
        validated = True
        for rule in self._get_current_version_rules(stage_name):
            validated = rule.validate_version(current_version)
            if not validated:
                return validated
        for rule in self._get_version_increment_rules(stage_name):
            validated = rule.validate_comparison([previous_version, current_version])
            if not validated:
                return validated
        for rule in self._get_manifest_versions_comparison_rules(stage_name):
            manifests = [
                m for m in
                self._get_manifests(stage_name)
                if m.name in rule.manifest_names
            ]
            if not manifests:
                continue
            versions = [m.version for m in manifests]
            validated = rule.validate_comparison(versions)
            if not validated:
                return validated
        return validated

    def _get_manifests(self, stage_name=None):
        manifests = self._manifests.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            manifests.extend(stage.manifests)
        return manifests
    
    def _get_current_version_rules(self, stage_name=None) -> list[SingleVersionRule]:
        rules = self._current_version_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.current_version_rules)
        return rules
    
    def _get_version_increment_rules(self, stage_name=None) -> list[VersionComparisonRule]:
        rules = self._version_increment_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.version_increment_rules)
        return rules

    def _get_manifest_versions_comparison_rules(self, stage_name=None) -> list[ManifestsComparisonRule]:
        rules = self._manifest_versions_comparison_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.manifest_versions_comparison_rules)
        return rules

    def _get_stage(self, stage_name):
        for stage in self._stages:
            if stage.name == stage_name:
                return stage
        raise ValueError(f"Stage {stage_name} not found.")
