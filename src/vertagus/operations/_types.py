import typing as T
from dataclasses import dataclass, field, asdict


class ProjectConfig(T.TypedDict):
    manifests: list[T.Type["ManifestConfig"]]
    rules: "RulesConfig"
    stages: dict[str, "StageConfig"]


class ManifestConfig(T.TypedDict):
    type: str
    path: str
    loc: T.Optional[str]


class RulesConfig(T.TypedDict):
    comparisons: T.Optional[list[str]]
    validations: T.Optional[list[str]]


class StageConfig(T.TypedDict):
    manifests: T.Optional[list[str]]
    rules: T.Optional["RulesConfig"]


@dataclass
class RulesData:
    comparisons: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)


@dataclass
class ManifestData:
    type: str
    path: str
    loc: str = field(default=None)

    def config(self):
        return dict(path=self.path, loc=self.loc)


@dataclass
class StageData:
    name: str
    manifests: list[ManifestData] = field(default_factory=list)
    rules: RulesData = field(default_factory=list)

    def config(self):
        return dict(
            name=self.name,
            manifests=[m.config() for m in self.manifests],
            validation_rules=self.rules.validations,
            comparison_rules=self.rules.comparisons,
        )


@dataclass
class ProjectData:
    manifests: list[ManifestData]
    rules: RulesData
    stages: dict[str, StageData]
