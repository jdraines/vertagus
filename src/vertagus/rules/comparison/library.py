from packaging import version
from vertagus.core.rule_bases import ComparisonRule


class Increasing(ComparisonRule):
    name = "any_increment"
    description = "Version must be greater than the previous one."

    def validate_comparison(self, versions: tuple[str, str]):
        version1, version2 = versions
        if not version1 and bool(version2):
            return True
        return version.parse(version1) < version.parse(version2)


class ManifestsComparisonRule(ComparisonRule):
    name = "manifests_comparison"
    description = "All manifests must have the same version."

    def __init__(self, config: dict):
        super().__init__(config)
        if "manifests" not in self.config:
            raise ValueError(
                "The `manifests_comparison` rule requires a `manifests` config listing "
                "the manifest names to compare, e.g.:\n\n"
                "    rules:\n"
                "      - type: manifests_comparison\n"
                "        config:\n"
                "          manifests: [pyproject, package_json]"
            )
        self.manifest_names = config["manifests"]

    def validate_comparison(self, versions: list[str]):
        if not versions:
            raise ValueError("No versions to compare.")
        if len(versions) == 1:
            raise ValueError("Only one version to compare. To compare, provide at least two versions.")
        return all([v == versions[0] for v in versions])
