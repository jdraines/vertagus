import typing as T
from vertagus.core.manifest_base import ManifestBase
from vertagus.core.rule_bases import ValidationRule, ComparisonRule


class Package:

    def __init__(self,
                 manifests: list[ManifestBase],
                 validation_rules=list[T.Type[ValidationRule]],
                 comparison_rules=list[T.Type[ComparisonRule]]
                 ):
        self._manifests = manifests or []
        self._validation_rules = validation_rules or []
        self._comparison_rules = comparison_rules or []
