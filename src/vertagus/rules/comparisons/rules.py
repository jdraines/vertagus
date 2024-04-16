from packaging import version
from vertagus.core.rule_bases import ComparisonRule


class Increasing(ComparisonRule):
    name = "increasing"

    @classmethod
    def compare(cls, value1, value2):
        return version.parse(value1) < version.parse(value2)
