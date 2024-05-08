import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule
from vertagus.rules.comparison.library import ManifestsComparisonRule
from vertagus.core.tag_base import AliasBase
from .package_base import Package


class Stage(Package):
    
    def __init__(self,
                 name: str,
                 manifests: list[ManifestBase],
                 current_version_rules: list[T.Type[SingleVersionRule]],
                 version_increment_rules: list[VersionComparisonRule],
                 manifest_versions_comparison_rules: list[ManifestsComparisonRule],
                 aliases: list[type[AliasBase]] = None
                 ):
        super().__init__(
            manifests=manifests,
            current_version_rules=current_version_rules,
            version_increment_rules=version_increment_rules,
            manifest_versions_comparison_rules=manifest_versions_comparison_rules
        )
        self.name = name
        self.aliases = aliases or []

    @property
    def current_version_rules(self):
        return self._current_version_rules
    
    @property
    def version_increment_rules(self):
        return self._version_increment_rules
    
    @property
    def manifest_versions_comparison_rules(self):
        return self._manifest_versions_comparison_rules
    
    @property
    def manifests(self):
        return self._manifests

    def get_version_aliases(self, version: str) -> list[AliasBase]:
        return [alias(version) for alias in self.aliases]
