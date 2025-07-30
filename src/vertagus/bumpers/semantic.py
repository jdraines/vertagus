import typing as T
import re
from packaging import version as versionmod

from ..core.bumper_base import BumperBase, BumperException
from ..core.scm_base import ScmBase


class SemverBumperException(BumperException):
    pass


class NoLevelSpecified(SemverBumperException):
    pass


class SemanticBumper(BumperBase):
    """
    Bumper that bumps versions according to semantic versioning rules.
    """

    name = "semver"

    def __init__(self, tag=None):
        super().__init__()
        self.tag = tag

    def _extract_mmp(self, version: versionmod.Version) -> tuple[int, int, int]:
        """
        Extract major, minor, and patch from a version string.
        """
        release = version.release
        if len(release) < 3:
            raise SemverBumperException(f"Invalid version format: {version}. Expected format is 'major.minor.patch'.")
        return release[0], release[1], release[2]

    def _extract_tag(self, version: versionmod.Version, versionstr: str) -> T.Union[str, None]:
        """
        Extract the tag from a version string.
        """
        v = version
        if not v.is_prerelease:
            return None
        if v.is_devrelease:
            if v.dev == 0:
                _version = versionstr.replace(v.base_version, "")
                if _version.endswith("dev"):
                    return "dev"
            return f"dev{v.dev}"
        if pre := v.pre:
            _tag = ""
            for part in pre:
                if isinstance(part, int):
                    _tag += str(part)
                else:
                    _tag += part
            return _tag
        raise SemverBumperException(f"Unable to extract tag from version: {version}.")

    def bump(self, version: str, level: T.Optional[str] = None) -> str:
        """
        Bump the version according to the specified level.
        """
        if level is None:
            raise NoLevelSpecified("Level must be specified. Use 'major', 'minor', 'patch', or 'tag'.")

        tag_sep = "."

        v = versionmod.parse(version)

        try:
            major, minor, patch = self._extract_mmp(v)
            tag = self._extract_tag(v, version)
        except Exception as e:
            raise ValueError(f"Invalid version format: {version}. Error: {e.__class__.__name__}: {e}") from e

        bumper = self._get_level_bumper(level)

        if tag is not None:
            _v = version.replace(tag, "")
            tag_sep = _v.replace(v.base_version, "")
        (major, minor, patch, tag) = bumper(int(major), int(minor), int(patch), tag)

        if tag is None:
            return f"{major}.{minor}.{patch}"
        else:
            return f"{major}.{minor}.{patch}{tag_sep}{tag}"

    def _get_level_bumper(self, level: str):
        _bumpers = {
            "major": self._bump_major,
            "minor": self._bump_minor,
            "patch": self._bump_patch,
            "tag": self._bump_tag,
        }
        if level not in _bumpers:
            raise SemverBumperException(f"Invalid level: {level}. Must be one of {list(_bumpers.keys())}.")
        return _bumpers[level]

    def _bump_major(self, major, minor, patch, tag):
        return major + 1, 0, 0, None

    def _bump_minor(self, major, minor, patch, tag):
        return major, minor + 1, 0, None

    def _bump_patch(self, major, minor, patch, tag):
        return major, minor, patch + 1, None

    def _bump_tag(self, major, minor, patch, tag):
        if tag is None:
            if self.tag is None:
                raise SemverBumperException("No tag specified and no existing tag to increment.")
            tag = f"{self.tag}0"
        match = re.match(r"(\D+)(\d+)", tag)
        if match:
            prefix, number = match.groups()
            if self.tag and self.tag != prefix:
                raise SemverBumperException(f"Tag prefix '{self.tag}' does not match existing tag prefix '{prefix}'.")
            number = int(number) + 1
            tag = f"{prefix}{number}"

        else:
            tag = f"{tag}1"
        return major, minor, patch, tag


class SemanticCommitBumper(SemanticBumper):
    """
    Bumper that uses semantic commit conventions:
    https://www.conventionalcommits.org/en/v1.0.0/
    """

    name = "semantic_commit"
    inject_scm = True

    def bump(self, version: str, scm: ScmBase, level: T.Optional[str] = None) -> str:
        """
        Bump the version according to the specified level for commit messages.
        """
        ordered_bumps = ["tag", "patch", "minor", "major"]
        determined_level = self.determine_bump_level(scm)
        if level is not None:
            if level != determined_level:
                if ordered_bumps.index(level) < ordered_bumps.index(determined_level):
                    raise SemverBumperException(
                        f"Specified level '{level}' is lower than determined level '{determined_level}'."
                    )
                determined_level = level
        return super().bump(version, determined_level)

    def determine_bump_level(self, scm: ScmBase, branch: T.Optional[str] = None) -> str:
        """
        Determine the bump level based on commit messages since the last tag.
        """
        commit_messages = scm.get_commit_messages_since_highest_version(branch)
        return self._get_level_from_conventional_commits(commit_messages)

    def _get_level_from_conventional_commits(self, commit_messages: list[str]):
        """
        Extract conventional commit types from commit messages.
        """
        ordered_bumps = ["patch", "minor", "major"]
        conventional_types = {
            "feat": "minor",
            "fix": "patch",
            "perf": "patch",
            "chore": "patch",
            "docs": "patch",
            "style": "patch",
            "refactor": "patch",
            "test": "patch",
        }
        levels = set()
        conventional_commits = self._extract_conventional_commits(commit_messages)
        for commit_type, scope, exclamation, description, breaking_change in conventional_commits:
            if commit_type.lower() in conventional_types:
                levels.add(conventional_types[commit_type.lower()])
                if exclamation:
                    levels.add("major")
                if breaking_change:
                    levels.add("major")
            else:
                levels.add("patch")
        if not levels:
            return "patch"
        return ordered_bumps[max([ordered_bumps.index(level) for level in levels])]

    def _extract_conventional_commits(
        self, commit_messages: list[str]
    ) -> list[tuple[str, T.Optional[str], T.Optional[str], str]]:
        """
        Extract conventional commit messages from a list of commit messages.
        """
        conventional_commits = []
        pattern = re.compile(
            r"^(?P<type>[\w]+)(?:\((?P<scope>[\w-]+)\))?(?P<exclamation>!)?: (?P<description>.+)$", re.DOTALL
        )
        for message in commit_messages:
            if match := pattern.match(message):
                commit_type = match.group("type")
                scope = match.group("scope")
                exclamation = match.group("exclamation")
                description = match.group("description")
                breaking_change = "BREAKING CHANGE" in message
                conventional_commits.append((commit_type, scope, exclamation, description, breaking_change))
        return conventional_commits
