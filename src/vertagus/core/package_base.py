import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import SingleVersionRule, VersionComparisonRule


class Package:

    def __init__(self,
                 manifests: list[ManifestBase],
                 current_version_rules: list[T.Type[SingleVersionRule]],
                 version_increment_rules: list[T.Type[VersionComparisonRule]],
                 manifest_versions_comparison_rules: list[T.Type[VersionComparisonRule]]
                 ):
        self._manifests = manifests or []
        self._current_version_rules = current_version_rules or []
        self._version_increment_rules = version_increment_rules or []
        self._manifest_versions_comparison_rules = manifest_versions_comparison_rules or []
