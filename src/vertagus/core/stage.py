import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import ValidationRule, ComparisonRule
from .package_base import Package


class Stage(Package):
    
    def __init__(self,
                 name: str,
                 manifests: list[ManifestBase],
                 validation_rules: list[T.Type[ValidationRule]],
                 comparison_rules: list[T.Type[ComparisonRule]],
                 ):
        super().__init__(manifests, validation_rules, comparison_rules)
        self.name = name

    @property
    def validation_rules(self):
        return self._validation_rules
    
    @property
    def comparison_rules(self):
        return self._comparison_rules
    
    @property
    def manifests(self):
        return self._manifests
