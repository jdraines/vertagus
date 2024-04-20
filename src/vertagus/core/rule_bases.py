import typing as T


class Rule:
    name: str = "base"


class VersionComparisonRule(Rule):

    def __init__(self, config: dict):
        self.config = config

    def validate_comparison(self, versions: T.Sequence[str]):
        raise NotImplementedError(
            'Method `validate_comparison` must be implemented in subclass'
        )
    

class SingleVersionRule(Rule):

    @classmethod
    def validate_version(cls, version: str):
        raise NotImplementedError(
            'Method validate must be implemented in subclass'
        )
