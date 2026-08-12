import json
import typing as T


class Rule:
    name: str = "base"
    description: str = "Base class for all rules"

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def __eq__(self, other):
        return type(self) is type(other) and self.config == other.config

    def __hash__(self):
        return hash((type(self), json.dumps(self.config, default=str, sort_keys=True)))


class SingleVersionRule(Rule):
    def validate_version(self, version: str) -> bool:
        raise NotImplementedError("Method validate_version must be implemented in subclass")


class ComparisonRule(Rule):
    def validate_comparison(self, versions: T.Sequence[str]) -> bool:
        raise NotImplementedError("Method validate_comparison must be implemented in subclass")
