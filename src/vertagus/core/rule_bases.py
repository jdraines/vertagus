import typing as T
import json


class Rule:
    name: str = "base"
    description: str = "Base class for all rules"


class VersionComparisonRule(Rule):
    def __init__(self, config: dict):
        self.config = config

    def validate_comparison(self, versions: T.Sequence[str]):
        raise NotImplementedError("Method `validate_comparison` must be implemented in subclass")

    def __hash__(self):
        return hash(json.dumps(self.__dict__, default=str, sort_keys=True))


class SingleVersionRule(Rule):
    @classmethod
    def validate_version(cls, version: str):
        raise NotImplementedError("Method validate must be implemented in subclass")


class ConfigurableSingleVersionRule(Rule):

    def __init__(self, config: dict):
        self.config = config
    
    def validate_version(self, version: str):
        raise NotImplementedError("Method validate must be implemented in subclass")


SingleVersionRuleType = T.Union[
    T.Type[SingleVersionRule],
    T.Type[ConfigurableSingleVersionRule],
]

SingleVersionRuleProtocol = T.Union[
    T.Type[SingleVersionRule],
    ConfigurableSingleVersionRule,
]

def is_single_version_rule_type(obj: T.Any) -> bool:
    return isinstance(obj, type) and issubclass(obj, (SingleVersionRule, ConfigurableSingleVersionRule))

def is_configurable_single_version_rule(obj: T.Any) -> bool:
    return isinstance(obj, ConfigurableSingleVersionRule) or (
        isinstance(obj, type) and issubclass(obj, ConfigurableSingleVersionRule)
    )
