import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.rules.comparison.library import ManifestsComparisonRule
from vertagus.core.rule_bases import SingleVersionRuleProtocol, VersionComparisonRule


class Package:
    def __init__(
        self,
        manifests: list[ManifestBase],
        current_version_rules: list[SingleVersionRuleProtocol],
        version_increment_rules: list[VersionComparisonRule],
        manifest_versions_comparison_rules: T.Sequence[ManifestsComparisonRule],
    ):
        self._manifests = manifests or []
        self._current_version_rules = current_version_rules or []
        self._version_increment_rules = version_increment_rules or []
        self._manifest_versions_comparison_rules = manifest_versions_comparison_rules or []
