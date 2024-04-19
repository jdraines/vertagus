import typing as T
from dataclasses import dataclass, field, asdict

class ScmConfigBase(T.TypedDict):
    scm_type: str


ScmConfig = T.TypeAlias(T.Union[ScmConfigBase, dict])


class ProjectConfig(T.TypedDict):
    manifests: list[T.Type["ManifestConfig"]]
    rules: "RulesConfig"
    stages: dict[str, "StageConfig"]


class ManifestConfig(T.TypedDict):
    type: str
    path: str
    loc: T.Optional[str]


class ManifestComparisonConfig(T.TypedDict):
    manifests: list[str]


class RulesConfig(T.TypedDict):
    current: list[str]
    increment: list[str]
    manifest_comparisons: list[ManifestComparisonConfig]


class StageConfig(T.TypedDict):
    manifests: T.Optional[list[str]]
    rules: T.Optional["RulesConfig"]
    aliases: T.Optional[list[str]]


class MasterConfig(T.TypedDict):
    project: ProjectConfig
    scm: T.Union[ScmConfigBase, dict]


@dataclass
class RulesData:
    current: list[str] = field(default_factory=list)
    increment: list[str] = field(default_factory=list)
    manifest_comparisons: list[ManifestComparisonConfig] = field(default_factory=list)


@dataclass
class ManifestData:
    type: str
    path: str
    loc: str = field(default=None)

    def config(self):
        return dict(path=self.path, loc=self.loc)


@dataclass
class StageData:
    name: str = field(default=None)
    manifests: list[ManifestData] = field(default_factory=list)
    rules: RulesData = field(default_factory=RulesData)
    aliases: list[str] = field(default_factory=list)

    def config(self):
        return dict(
            name=self.name,
            manifests=[m.config() for m in self.manifests],
            current_version_rules=self.rules.current,
            version_increment_rules=self.rules.increment,
            manifest_versions_comparison_rules=self.rules.manifest_comparisons,
            aliases=self.aliases,
        )

@dataclass
class ProjectData:
    manifests: list[ManifestData]
    rules: RulesData
    stages: dict[str, StageData]

    def config(self):
        return dict(
            manifests=[m.config() for m in self.manifests],
            stages = [stage.config() for stage in self.stages.values()],
            current_version_rules=self.rules.current,
            version_increment_rules=self.rules.increment,
            manifest_versions_comparison_rules=self.rules.manifest_comparisons,
        )
    

@dataclass
class ScmData:
    scm_type: str
    kwargs: dict

    def config(self):
        return self.kwargs
