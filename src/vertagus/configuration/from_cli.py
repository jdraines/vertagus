"""Build a vertagus configuration from CLI options, without a configuration file.

The CLI can assemble the same :class:`~vertagus.configuration.types.MasterConfig`
mapping that :mod:`vertagus.configuration.load` reads from disk, so that commands
work identically whether their settings came from ``vertagus.yaml`` or from flags
like ``--manifest`` and ``--rule``.
"""

import copy
import json
import os
import typing as T
from dataclasses import dataclass

from vertagus.errors import ConfigurationError

from .types import ManifestConfig, MasterConfig

DEFAULT_SCM_TYPE = "git"

_MANIFEST_TYPE_BY_FILENAME = {
    "pyproject.toml": "setuptools_pyproject",
}

_MANIFEST_TYPE_BY_EXTENSION = {
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
}

_MANIFEST_SPEC_KEYS = ("path", "type", "loc", "name")

# An scm manifest is not a project manifest and never carries a name, so accepting one
# would only let a `name=` silently go nowhere.
_SCM_MANIFEST_SPEC_KEYS = ("path", "type", "loc")

# Every option below is a single value that means nothing when empty; only --tag-prefix
# is meaningfully empty, as the way to say "this configuration has no tag prefix".
_NON_EMPTY_SCALAR_OPTIONS = (
    ("bumper", "--bumper"),
    ("root", "--root"),
    ("scm_type", "--scm-type"),
    ("version_strategy", "--version-strategy"),
    ("target_branch", "--target-branch"),
    ("scm_manifest", "--scm-manifest"),
)


@dataclass
class CliConfigOptions:
    """The configuration-defining options accepted by the vertagus commands."""

    manifest: tuple[str, ...] = ()
    rule: tuple[str, ...] = ()
    alias: tuple[str, ...] = ()
    bumper: str | None = None
    root: str | None = None
    scm_type: str | None = None
    tag_prefix: str | None = None
    version_strategy: str | None = None
    target_branch: str | None = None
    scm_manifest: str | None = None

    def any_provided(self) -> bool:
        """Whether the user supplied any configuration on the command line.

        A scalar option counts as supplied whenever it was passed at all, empty string
        included, so that ``--tag-prefix ''`` — the way to say "no tag prefix" — is not
        mistaken for an option the user left off.
        """
        scalars = (
            self.bumper,
            self.root,
            self.scm_type,
            self.tag_prefix,
            self.version_strategy,
            self.target_branch,
            self.scm_manifest,
        )
        return any([self.manifest, self.rule, self.alias]) or any(value is not None for value in scalars)


def infer_manifest_type(path: str) -> str:
    """Guess a manifest type from a file name, e.g. ``pyproject.toml`` -> ``setuptools_pyproject``."""
    basename = os.path.basename(path).lower()
    if basename in _MANIFEST_TYPE_BY_FILENAME:
        return _MANIFEST_TYPE_BY_FILENAME[basename]
    extension = os.path.splitext(basename)[1]
    if extension in _MANIFEST_TYPE_BY_EXTENSION:
        return _MANIFEST_TYPE_BY_EXTENSION[extension]
    raise ConfigurationError(
        f"Could not determine the manifest type of {path!r}. Pass it explicitly, e.g. "
        f"--manifest 'path={path},type=yaml'. Run `vertagus list-manifests` to see the available types."
    )


def parse_manifest_spec(spec: str, index: int = 0, base_dir: str | None = None) -> ManifestConfig:
    """Parse a ``--manifest`` value.

    A spec is either a bare path (``src/pyproject.toml``) or a comma-separated list of
    ``key=value`` pairs (``path=version.json,type=json,loc=project.version``). Supported
    keys are ``path``, ``type``, ``loc`` and ``name``. The type is inferred from the file
    name when it is omitted, and the name defaults to ``manifest_<n>``.

    Relative paths are resolved against ``base_dir`` (the current directory by default) so
    that a manifest named on the command line always means what the user typed, regardless
    of where any configuration file lives.
    """
    fields = _parse_spec_fields(spec, valid_keys=_MANIFEST_SPEC_KEYS, spec_name="manifest")
    path = fields.get("path")
    if not path:
        raise ConfigurationError(f"Invalid manifest {spec!r}: no path was given.")

    manifest_type = fields.get("type") or infer_manifest_type(path)
    manifest: ManifestConfig = {
        "name": fields.get("name") or f"manifest_{index + 1}",
        "type": manifest_type,
        "path": os.path.abspath(os.path.join(base_dir or os.getcwd(), path)),
        "loc": fields.get("loc"),
    }
    return manifest


def parse_rule_spec(spec: str) -> str | dict:
    """Parse a ``--rule`` value.

    A rule is either a bare name (``not_empty``) or a name and a JSON object holding its
    configuration, separated by a colon (``regex:{"pattern": "^\\\\d+"}``).
    """
    name, separator, raw_config = spec.partition(":")
    name = name.strip()
    if not name:
        raise ConfigurationError(f"Invalid rule {spec!r}: no rule name was given.")
    if not separator:
        return name
    try:
        config = json.loads(raw_config)
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid rule {spec!r}: the configuration after ':' is not valid JSON ({e}). "
            f'Expected something like --rule \'{name}:{{"key": "value"}}\'.'
        ) from e
    if not isinstance(config, dict):
        raise ConfigurationError(
            f"Invalid rule {spec!r}: the configuration after ':' must be a JSON object, got {type(config).__name__}."
        )
    return {"type": name, "config": config}


def build_config_overlay(opts: CliConfigOptions) -> dict:
    """Build a partial :class:`MasterConfig` holding only the settings the user supplied."""
    _reject_empty_scalars(opts)
    overlay: dict[str, dict] = {"scm": {}, "project": {}}

    if opts.scm_type:
        overlay["scm"]["type"] = opts.scm_type
    if opts.tag_prefix is not None:
        overlay["scm"]["tag_prefix"] = opts.tag_prefix
    if opts.version_strategy:
        overlay["scm"]["version_strategy"] = opts.version_strategy
    if opts.target_branch:
        overlay["scm"]["target_branch"] = opts.target_branch
    if opts.scm_manifest:
        overlay["scm"].update(_parse_scm_manifest_spec(opts.scm_manifest))

    if opts.manifest:
        base_dir = os.path.abspath(opts.root) if opts.root else None
        overlay["project"]["manifests"] = [
            parse_manifest_spec(spec, index=i, base_dir=base_dir) for i, spec in enumerate(opts.manifest)
        ]
    if opts.rule:
        overlay["project"]["rules"] = [parse_rule_spec(spec) for spec in opts.rule]
    if opts.alias:
        overlay["project"]["aliases"] = list(opts.alias)
    if opts.bumper:
        overlay["project"]["bumper"] = {"type": opts.bumper}
    if opts.root:
        overlay["project"]["root"] = os.path.abspath(opts.root)

    return overlay


def build_master_config(opts: CliConfigOptions) -> MasterConfig:
    """Build a complete configuration from command line options alone."""
    overlay = build_config_overlay(opts)
    config: MasterConfig = {
        "scm": {"type": DEFAULT_SCM_TYPE, **overlay["scm"]},  # type: ignore[typeddict-item]
        "project": {"root": os.getcwd(), **overlay["project"]},  # type: ignore[typeddict-item]
    }

    manifests = config["project"].get("manifests")
    if not manifests:
        raise ConfigurationError(
            "No manifests were configured. Either create a vertagus configuration file "
            "(`vertagus init`) or name a manifest on the command line, e.g. "
            "--manifest pyproject.toml."
        )

    _apply_scm_manifest_default(config, manifests)
    return config


def merge_config(base: MasterConfig, opts: CliConfigOptions) -> MasterConfig:
    """Overlay command line options onto a configuration loaded from a file.

    Settings named on the command line replace their counterparts in the file. Options
    that accept multiple values replace the file's list outright rather than adding to it.
    """
    overlay = build_config_overlay(opts)
    merged = copy.deepcopy(base)
    for section, values in overlay.items():
        if not values:
            continue
        section_config = merged.get(section) or {}
        section_config.update(values)
        merged[section] = section_config  # type: ignore[literal-required]
    if opts.manifest:
        # The manifests came from the command line, so the branch-strategy default reads
        # the same way it does without a configuration file.
        _apply_scm_manifest_default(merged, overlay["project"]["manifests"])
    return merged


def _apply_scm_manifest_default(config: MasterConfig, manifests: list[ManifestConfig]) -> None:
    """Point a branch-strategy SCM at the first project manifest when it has none of its own.

    The manifest that declares the version is usually the same file on both sides, and
    naming it twice on the command line is pure ceremony.

    The SCM reads this path out of source control rather than off disk, so it has to be
    relative to the repository — which is the SCM's own root, not the project root. The
    two differ whenever ``--root`` points into a subdirectory of the repository.
    """
    scm = config["scm"]
    if scm.get("version_strategy") != "branch" or scm.get("manifest_path"):
        return
    primary = manifests[0]
    scm["manifest_path"] = _repo_relative_path(primary["path"], scm.get("root"))
    scm["manifest_type"] = primary["type"]
    if primary.get("loc"):
        scm["manifest_loc"] = primary["loc"]


def _repo_relative_path(path: str, scm_root: str | None) -> str:
    """Express an absolute manifest path the way source control addresses it.

    Paths are resolved against the SCM root, and always with forward slashes, since that
    is how git names a file in ``git show <ref>:<path>`` on every platform.
    """
    relative = os.path.relpath(path, scm_root or os.getcwd())
    return relative.replace(os.sep, "/")


def _reject_empty_scalars(opts: CliConfigOptions) -> None:
    """Reject single-valued options passed as an empty string, which cannot mean anything."""
    for attribute, flag in _NON_EMPTY_SCALAR_OPTIONS:
        if getattr(opts, attribute) == "":
            raise ConfigurationError(f"Invalid {flag}: the value is empty.")


def _parse_scm_manifest_spec(spec: str) -> dict[str, T.Any]:
    """Parse ``--scm-manifest`` into the ``manifest_*`` keys of the scm configuration.

    Unlike project manifests, this path is read out of source control rather than off
    disk, so it stays exactly as the user wrote it: relative to the repository root.
    """
    fields = _parse_spec_fields(spec, valid_keys=_SCM_MANIFEST_SPEC_KEYS, spec_name="scm manifest")
    path = fields.get("path")
    if not path:
        raise ConfigurationError(f"Invalid scm manifest {spec!r}: no path was given.")
    scm_config: dict[str, T.Any] = {
        "manifest_path": path,
        "manifest_type": fields.get("type") or infer_manifest_type(path),
    }
    if fields.get("loc"):
        scm_config["manifest_loc"] = fields["loc"]
    return scm_config


def _parse_spec_fields(spec: str, valid_keys: tuple[str, ...], spec_name: str) -> dict[str, str]:
    """Parse a bare path or a comma-separated ``key=value`` spec into a mapping.

    A value is read as a spec when it opens with one of ``valid_keys``, and as a bare path
    when it holds no ``=`` at all. Anything else is ambiguous — a misspelled key and a path
    containing an ``=`` look alike — so it is rejected rather than guessed at. Keys given
    without a value are dropped, leaving the same defaults as leaving the key off entirely.
    """
    spec = spec.strip()
    if not spec:
        raise ConfigurationError(f"Invalid {spec_name}: the value is empty.")
    if "=" not in spec:
        return {"path": spec}
    if spec.split(",", 1)[0].partition("=")[0].strip() not in valid_keys:
        raise ConfigurationError(
            f"Invalid {spec_name} {spec!r}: a 'key=value' spec must open with one of "
            f"{', '.join(valid_keys)}. If this is a path that contains an '=', write it as "
            f"'path={spec}'."
        )

    fields: dict[str, str] = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        key, separator, value = part.partition("=")
        key = key.strip()
        if not separator:
            raise ConfigurationError(
                f"Invalid {spec_name} {spec!r}: expected 'key=value' pairs separated by commas, but found {part!r}."
            )
        if key not in valid_keys:
            raise ConfigurationError(
                f"Invalid {spec_name} {spec!r}: unknown key {key!r}. Valid keys are: {', '.join(valid_keys)}."
            )
        value = value.strip()
        if value:
            fields[key] = value
    return fields
