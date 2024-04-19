from packaging import version
from vertagus.core.rule_bases import VersionComparisonRule


class Increasing(VersionComparisonRule):
    name = "increasing"

    @classmethod
    def validate_comparison(cls, versions: tuple[str, str]):
        version1, version2 = versions
        return version.parse(version1) < version.parse(version2)
