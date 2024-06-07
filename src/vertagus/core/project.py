import typing as T
from logging import getLogger

from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.rules.comparison.library import ManifestsComparisonRule
from vertagus.core.tag_base import AliasBase
from .package_base import Package
from .stage import Stage


logger = getLogger(__name__)


class Project(Package):
    
    def __init__(self,
                 manifests: list[ManifestBase],
                 current_version_rules: list[T.Type[SingleVersionRule]],
                 version_increment_rules: list[VersionComparisonRule],
                 manifest_versions_comparison_rules: list[ManifestsComparisonRule],
                 stages: list[Stage] = None,
                 aliases: list[type[AliasBase]] = None
                 ):
        super().__init__(
            manifests=manifests,
            current_version_rules=current_version_rules,
            version_increment_rules=version_increment_rules,
            manifest_versions_comparison_rules=manifest_versions_comparison_rules
        )
        self._stages = stages or []
        self.aliases = aliases or []
    @property
    def stages(self):
        return self._stages
    
    def get_version(self, stage_name: str = None):
        manifests = self._get_manifests(stage_name)
        if not manifests:
            raise ValueError("No manifests found.")
        return manifests[0].version

    def get_aliases(self, stage_name: str = None) -> list[AliasBase]:
        version = self.get_version()
        aliases = self._get_version_aliases(version)
        if stage_name:
            stage = self._get_stage(stage_name)
            aliases.extend(stage.get_version_aliases(version))
        return list(dict.fromkeys(aliases).keys())

    def validate_version(self, previous_version: str, stage_name: str = None):
        primary_manifest = self._get_manifests(stage_name)[0]
        current_version = self.get_version(stage_name)
        logger.info(
            f"Validating version for manifest {primary_manifest.name!r}\n"
            f"  manifest_type={primary_manifest.manifest_type!r}\n"
            f"  path={primary_manifest.path}\n"
            f"  version loc={primary_manifest.loc}\n"
            f"  previous_version={previous_version}\n"
            f"  current_version={current_version}\n"
            f"  stage_name={stage_name}"
        )
        validated = self._run_current_version_rules(current_version, stage_name)
        if not validated:
            return validated
        validated = self._run_version_increment_rules(previous_version, current_version, stage_name)
        if not validated:
            return validated
        return self._run_manifest_versions_comparison_rules(stage_name)

    def _get_version_aliases(self, version: str) -> list[AliasBase]:
        return [alias(version) for alias in self.aliases]

    def _run_current_version_rules(self, current_version, stage_name=None):
        validated = True
        for rule in self._get_current_version_rules(stage_name):
            logger.info(
                f"Validating rule {rule.name!r} for {current_version}"
            )
            validated = rule.validate_version(current_version)
            if not validated:
                logger.error(
                    f"Validation failed for rule {rule.name!r}: {rule.description}"
                )
                return validated
        return validated

    def _run_version_increment_rules(self, previous_version, current_version, stage_name=None):
        validated = True
        versions = [previous_version, current_version]
        for rule in self._get_version_increment_rules(stage_name):
            logger.info(
                f"Validating rule {rule.name!r} for {versions}"
            )
            validated = rule.validate_comparison(versions)
            if not validated:
                logger.error(
                    f"Validation failed for rule  {rule.name!r}: {rule.description}"
                )
                return validated
        return validated

    def _run_manifest_versions_comparison_rules(self, stage_name=None):
        validated = True
        for rule in self._get_manifest_versions_comparison_rules(stage_name):
            if not rule.manifest_names:
                continue
            manifests = [
                m for m in
                self._get_manifests(stage_name)
                if m.name in rule.manifest_names
            ]
            if not manifests:
                raise ValueError(f"Manifests {rule.manifest_names} not found.")
            versions = [m.version for m in manifests]
            logger.info(
                f"Validating rule {rule.name!r} for {versions}"
            )
            validated = rule.validate_comparison(versions)
            if not validated:
                logger.error(
                    f"Validation failed for rule {rule.name!r}: {rule.description}"
                )
                return validated
        return validated

    def _get_manifests(self, stage_name=None):
        manifests = self._manifests.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            manifests.extend(stage.manifests)
        return list(dict.fromkeys(manifests).keys())
    
    def _get_current_version_rules(self, stage_name=None) -> list[SingleVersionRule]:
        rules = self._current_version_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.current_version_rules)
        return list(dict.fromkeys(rules).keys())
    
    def _get_version_increment_rules(self, stage_name=None) -> list[VersionComparisonRule]:
        rules = self._version_increment_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.version_increment_rules)
        return list(dict.fromkeys(rules).keys())

    def _get_manifest_versions_comparison_rules(self, stage_name=None) -> list[ManifestsComparisonRule]:
        rules = self._manifest_versions_comparison_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.manifest_versions_comparison_rules)
        return list(dict.fromkeys(rules).keys())

    def _get_stage(self, stage_name):
        for stage in self._stages:
            if stage.name == stage_name:
                return stage
        raise ValueError(f"Stage {stage_name} not found.")
