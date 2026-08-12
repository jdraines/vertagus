import typing as T
from dataclasses import dataclass, field
import os

from vertagus.errors import ConfigurationError

V = T.TypeVar("V", bound=T.Any)


def getdefault(d: T.Mapping[str, T.Any], k: str, default: V) -> V:
    """
    Get a value from a dictionary, returning a default if the key is not present.
    """
    r: V | T.Any = d.get(k, default)
    if r is None:
        r = default
    return r


class TypeAndConfig(T.TypedDict):
    type: str
    config: dict


class ScmConfigBase(T.TypedDict):
    type: str
    version_strategy: T.Literal["tag", "branch"] | None
    target_branch: str | None
    manifest_path: str | None
    manifest_type: str | None
    manifest_loc: str | list[str] | None


ScmConfig = ScmConfigBase | dict


class BumperConfig(T.TypedDict):
    type: str
    tag: str | None


class ProjectConfig(T.TypedDict):
    manifests: list["ManifestConfig"]
    rules: "RulesConfig"
    stages: dict[str, "StageConfig"]
    aliases: list[str] | None
    root: str | None
    bumper: BumperConfig | None


class ManifestConfig(T.TypedDict):
    name: str
    type: str
    path: str
    loc: str | list[str] | None


RulesConfig = list[str | TypeAndConfig]


class StageConfig(T.TypedDict):
    name: str
    manifests: list[ManifestConfig] | None
    rules: RulesConfig | None
    aliases: list[str] | None
    bumper: BumperConfig | None


class MasterConfig(T.TypedDict):
    project: ProjectConfig
    scm: ScmConfigBase


_OLD_RULES_FORMAT_MESSAGE = """\
Invalid `rules` configuration: expected a flat list of rules, but found a mapping \
with the key(s) {keys}.

The config schema changed in vertagus 0.5.0. Rules are no longer grouped under \
`current`, `increment`, or `manifest_comparisons`. List them all directly under \
`rules` instead, and vertagus will work out what each rule does.

Before (0.4.x):

    rules:
      current:
        - not_empty
      increment:
        - any_increment

After (0.5.0):

    rules:
      - not_empty
      - any_increment

See https://github.com/jdraines/vertagus/blob/main/docs/configuration.md for details.\
"""


@dataclass
class RulesData:
    rules: list[str | dict] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.rules, dict):
            keys = ", ".join(repr(k) for k in self.rules)
            raise ConfigurationError(_OLD_RULES_FORMAT_MESSAGE.format(keys=keys))


@dataclass
class ManifestData:
    name: str
    type: str
    path: str
    loc: list[str] | None = None

    class _OutputConfig(T.TypedDict):
        name: str
        path: str
        loc: list[str] | None

    def __init__(self, name: str, type: str, path: str, loc: list[str] | str | None = None):
        self.name = name
        self.type = type
        self.path = path
        self.loc = self._parse_loc(loc)

    def _parse_loc(self, loc: list[str] | str | None) -> list[str] | None:
        if isinstance(loc, str):
            return loc.split(".")
        return loc

    def config(self) -> _OutputConfig:
        return self._OutputConfig(name=self.name, path=self.path, loc=self.loc)


class BumperData:
    def __init__(self, type: str, **kwargs: T.Any):
        self.type: str = type
        self._kwargs = kwargs

    def config(self) -> dict[str, T.Any]:
        return dict(type=self.type, **self._kwargs)

    def kwargs(self) -> dict[str, T.Any]:
        return self._kwargs


class StageData:
    def __init__(
        self,
        name: str,
        manifests: list[ManifestData],
        rules: RulesData,
        aliases: list[str] | None = None,
        bumper: BumperData | None = None,
    ):
        self.name: str = name
        self.manifests: list[ManifestData] = manifests
        self.rules: RulesData = rules
        self.aliases: list[str] | None = aliases
        self.bumper: BumperData | None = bumper

    @classmethod
    def from_stage_config(cls, name: str, config: StageConfig):
        manifest_configs: list[ManifestConfig] = config.get("manifests", []) or []
        bumper_data = None
        bumper_config = getdefault(config, "bumper", None)
        if bumper_config:
            bumper_data = BumperData(**bumper_config)
        return cls(
            name=name,
            manifests=[ManifestData(**m) for m in manifest_configs],
            rules=RulesData(
                rules=getdefault(config, "rules", []),
            ),
            aliases=config.get("aliases", []),
            bumper=bumper_data,
        )

    def config(self):
        return dict(
            name=self.name,
            manifests=[m.config() for m in self.manifests],
            rules=self.rules.rules,
            aliases=self.aliases,
            bumper=self.bumper.config() if self.bumper else None,
        )


class ProjectData:
    def __init__(
        self,
        manifests: list[ManifestData],
        rules: RulesData,
        stages: list[StageData] | None = None,
        aliases: list[str] | None = None,
        root: str | None = None,
        bumper: BumperData | None = None,
    ):
        self.manifests: list[ManifestData] = manifests
        self.rules: RulesData = rules
        self.stages: list[StageData] | None = stages
        self.aliases: list[str] | None = aliases
        self.root: str | None = root or os.getcwd()
        self.bumper: BumperData | None = bumper

    def config(self):
        stages = self.stages or []

        return dict(
            manifests=[m.config() for m in self.manifests],
            stages=[stage.config() for stage in stages],
            rules=self.rules.rules,
            aliases=self.aliases,
            root=self.root,
            bumper=self.bumper.config() if self.bumper else None,
        )

    @classmethod
    def from_project_config(cls, config: ProjectConfig):
        stages = config.get("stages", {})
        manifests: list[ManifestConfig] = config.get("manifests", [])
        bumper_data = None
        bumper_config = getdefault(config, "bumper", None)
        if bumper_config:
            bumper_data = BumperData(**bumper_config)
        return cls(
            manifests=[ManifestData(**m) for m in manifests],
            rules=RulesData(
                rules=config.get("rules", []),
            ),
            stages=[StageData.from_stage_config(name, data) for name, data in stages.items()],
            aliases=config.get("aliases", []),
            root=config.get("root", None),
            bumper=bumper_data,
        )


class ScmData:
    def __init__(
        self,
        type: str,
        root: str | None = None,
        version_strategy: T.Literal["tag", "branch"] | None = "tag",
        target_branch: str | None = None,
        manifest_path: str | None = None,
        manifest_type: str | None = None,
        manifest_loc: str | list[str] | None = None,
        **kwargs,
    ):
        self.scm_type = type
        self.root = root
        self.version_strategy = version_strategy or "tag"
        self.target_branch = target_branch
        self.manifest_path = manifest_path
        self.manifest_type = manifest_type
        self.manifest_loc: list[str] | None = self._parse_manifest_loc(manifest_loc)
        self.kwargs = kwargs

    def config(self) -> dict[str, T.Any]:
        config_dict: dict[str, T.Any] = dict(root=self.root, version_strategy=self.version_strategy, **self.kwargs)
        if self.target_branch:
            config_dict["target_branch"] = self.target_branch
        if self.manifest_path:
            config_dict["manifest_path"] = self.manifest_path
        if self.manifest_type:
            config_dict["manifest_type"] = self.manifest_type
        if self.manifest_loc:
            config_dict["manifest_loc"] = self.manifest_loc
        return config_dict

    def _parse_manifest_loc(self, manifest_loc) -> list[str] | None:
        """
        Parse the manifest location into a list of strings.
        """
        if isinstance(manifest_loc, str):
            return manifest_loc.split(".")
        return manifest_loc
