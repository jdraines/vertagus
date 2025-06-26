import typing as T
from dataclasses import dataclass, field
import os

V = T.TypeVar('V', bound=T.Any)
DictType = T.Union[T.Dict, T.TypedDict]


def getdefault(d: DictType, k: str, default: V)  -> V:
    """
    Get a value from a dictionary, returning a default if the key is not present.
    """
    r: T.Union[V, T.Any] = d.get(k, default)
    if r is None:
        r = default
    return r


class ScmConfigBase(T.TypedDict):
    scm_type: str
    # New fields for branch-based version checking
    version_strategy: T.Optional[str]  # "tag" (default) or "branch"
    target_branch: T.Optional[str]  # Branch to compare against when using branch strategy
    manifest_path: T.Optional[str]  # Path to the manifest file relative to repo root
    manifest_type: T.Optional[str]  # Type of manifest (e.g., 'set
    manifest_loc: T.Optional[str]   # A dot-separated string representing the location of the version in the manifest file

ScmConfig = T.Union[ScmConfigBase, dict]


class ProjectConfig(T.TypedDict):
    manifests: list["ManifestConfig"]
    rules: "RulesConfig"
    stages: dict[str, "StageConfig"]
    aliases: T.Optional[list[str]]
    root: T.Optional[str]


class ManifestConfig(T.TypedDict):
    name: str
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
    name: str
    manifests: T.Optional[list[ManifestConfig]]
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
    name: str
    type: str
    path: str
    loc: T.Optional[list[str]] = None

    class _OutputConfig(T.TypedDict):
        name: str
        path: str
        loc: T.Optional[list[str]]

    def __init__(self, name: str, type: str, path: str, loc: T.Union[list[str], str, None] = None):
        self.name = name
        self.type = type
        self.path = path
        self.loc = self._parse_loc(loc)

    def _parse_loc(self, loc: T.Union[list[str], str, None]) -> T.Optional[list[str]]:
        if isinstance(loc, str):
            return loc.split(".")
        return loc

    def config(self) -> _OutputConfig:
        return self._OutputConfig(name=self.name, path=self.path, loc=self.loc)


class StageData:

    def __init__(self,
                 name: str,
                 manifests: list[ManifestData],
                 rules: RulesData,
                 aliases: T.Optional[list[str]] = None
                 ):
        self.name: str = name
        self.manifests: list[ManifestData] = manifests
        self.rules: RulesData = rules
        self.aliases: T.Optional[list[str]] = aliases

    @classmethod
    def from_stage_config(cls, name: str, config: StageConfig):
        manifest_configs: list[ManifestConfig] = config.get("manifests", []) or []
        return cls(
            name=name,
            manifests=[ManifestData(**m) for m in manifest_configs],
            rules=RulesData(
                current=getdefault(getdefault(config, "rules", {}), "current", []),
                increment=getdefault(getdefault(config, "rules", {}), "increment", []),
                manifest_comparisons=getdefault(getdefault(config, "rules", {}), "manifest_comparisons", []),
            ),
            aliases=config.get("aliases", []),
        )

    def config(self):
        return dict(
            name=self.name,
            manifests=[m.config() for m in self.manifests],
            current_version_rules=self.rules.current,
            version_increment_rules=self.rules.increment,
            manifest_versions_comparison_rules=self.rules.manifest_comparisons,
            aliases=self.aliases,
        )


class ProjectData:
    
    def __init__(self,
                 manifests: list[ManifestData],
                 rules: RulesData,
                 stages: T.Optional[list[StageData]] = None,
                 aliases: T.Optional[list[str]] = None,
                 root: T.Optional[str] = None 
                 ):
        self.manifests: list[ManifestData] = manifests
        self.rules: RulesData = rules
        self.stages: T.Optional[list[StageData]] = stages
        self.aliases: T.Optional[list[str]] = aliases
        self.root: T.Optional[str] = root or os.getcwd()

    def config(self):
        stages = self.stages or []
        return dict(
            manifests=[m.config() for m in self.manifests],
            stages=[stage.config() for stage in stages],
            current_version_rules=self.rules.current,
            version_increment_rules=self.rules.increment,
            manifest_versions_comparison_rules=self.rules.manifest_comparisons,
            aliases=self.aliases,
        )
    
    @classmethod
    def from_project_config(cls, config: ProjectConfig):
        stages = config.get("stages", {})
        manifests: list[ManifestConfig] = config.get("manifests", [])
        return cls(
            manifests=[ManifestData(**m) for m in manifests],
            rules=RulesData(
                current=config.get("rules", {}).get("current", []),
                increment=config.get("rules").get("increment", []),
                manifest_comparisons=config.get("rules").get("manifest_comparisons", []),
            ),
            stages=[StageData.from_stage_config(name, data) for name, data in stages.items()],
            aliases=config.get("aliases", []),
            root=config.get("root", None)
        )


class ScmData:
    
    def __init__(self,
                 type: str,
                 root: T.Optional[str] = None,
                 version_strategy: str = "tag", 
                 target_branch: T.Optional[str] = None,
                 manifest_path: T.Optional[str] = None, 
                 manifest_type: T.Optional[str] = None,
                 manifest_loc: T.Optional[str] = None,
                 **kwargs
                 ):
        self.scm_type = type
        self.root = root
        self.version_strategy = version_strategy  # "tag" or "branch"
        self.target_branch = target_branch
        self.manifest_path = manifest_path  # Required for branch strategy
        self.manifest_type = manifest_type  # Required for branch strategy
        self.manifest_loc = manifest_loc
        self.kwargs = kwargs

    def config(self):
        config_dict = dict(
            root=self.root,
            version_strategy=self.version_strategy,
            **self.kwargs
        )
        if self.target_branch:
            config_dict['target_branch'] = self.target_branch
        if self.manifest_path:
            config_dict['manifest_path'] = self.manifest_path
        if self.manifest_type:
            config_dict['manifest_type'] = self.manifest_type
        if self.manifest_loc:
            config_dict['manifest_loc'] = self.manifest_loc
        return config_dict
