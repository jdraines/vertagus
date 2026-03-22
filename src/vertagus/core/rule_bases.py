import typing as T
import json


class Rule:
    name: str = "base"
    description: str = "Base class for all rules"

    def __init__(self, config: T.Optional[dict] = None):
        self.config = config or {}


class SingleVersionRule(Rule):
    def validate_version(self, version: str) -> bool:
        raise NotImplementedError("Method validate_version must be implemented in subclass")


class ComparisonRule(Rule):
    def validate_comparison(self, versions: T.Sequence[str]) -> bool:
        raise NotImplementedError("Method validate_comparison must be implemented in subclass")

    def __hash__(self):
        return hash(json.dumps(self.__dict__, default=str, sort_keys=True))
