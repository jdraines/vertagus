import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import ValidationRule, ComparisonRule
from .package_base import Package
from .stage import Stage

class Project(Package):
    
    def __init__(self,
                 manifests: list[ManifestBase],
                 validation_rules: list[T.Type[ValidationRule]],
                 comparison_rules: list[T.Type[ComparisonRule]],
                 stages: list[Stage] = None
                 ):
        super().__init__(manifests, validation_rules, comparison_rules)
        self._stages = stages or []

    @property
    def stages(self):
        return self._stages
    
    def get_manifests(self, stage_name=None):
        manifests = self._manifests.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            manifests.extend(stage.manifests)
        return manifests
    
    def get_validation_rules(self, stage_name=None):
        rules = self._validation_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.validation_rules)
        return rules
    
    def get_comparison_rules(self, stage_name=None):
        rules = self._comparison_rules.copy()
        if stage_name:
            stage = self._get_stage(stage_name)
            rules.extend(stage.comparison_rules)
        return rules

    def _get_stage(self, stage_name):
        for stage in self._stages:
            if stage.name == stage_name:
                return stage
        raise ValueError(f"Stage {stage_name} not found.")