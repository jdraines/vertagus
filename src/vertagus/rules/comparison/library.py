from packaging import version
from vertagus.core.rule_bases import VersionComparisonRule


class Increasing(VersionComparisonRule):
    name = "any_increment"

    def validate_comparison(self, versions: tuple[str, str]):
        version1, version2 = versions
        if not version1 and bool(version2):
            return True
        return version.parse(version1) < version.parse(version2)


class ManifestsComparisonRule(VersionComparisonRule):
    name = "manifests_comparison"

    def __init__(self, config: dict):
        self.manifest_names = config["manifests"]

    def validate_comparison(self, versions: tuple[str, str]):
        if not versions:
            raise ValueError("No versions to compare.")
        if len(versions) == 1:
            raise ValueError("Only one version to compare. To compare, provide at least two versions.")
        return all([v == versions[0] for v in versions])
