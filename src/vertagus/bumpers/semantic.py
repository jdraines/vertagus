import typing as T
from ..core.bumper_base import BumperBase, BumperException
import re
from packaging import version as versionmod


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

    def bump(self, version: str, level: str = None) -> str:
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
            raise ValueError(
                f"Invalid version format: {version}. Error: "
                f"{e.__class__.__name__}: {e}"
            ) from e

        bumper = self._get_level_bumper(level)
        
        if tag is not None:
            _v = version.replace(tag, "")
            tag_sep = _v.replace(v.base_version, "")
        (
            major, minor, patch, tag
        ) = bumper(
            int(major), int(minor), int(patch), tag
        )

        if tag is None:
            return f"{major}.{minor}.{patch}"
        else:
            return f"{major}.{minor}.{patch}{tag_sep}{tag}"

    def _get_level_bumper(self, level: str):
        _bumpers = {
            "major": self._bump_major,
            "minor": self._bump_minor,
            "patch": self._bump_patch,
            "tag": self._bump_tag
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
        match = re.match(r'(\D+)(\d+)', tag)
        if match:
            prefix, number = match.groups()
            if self.tag and self.tag != prefix:
                raise SemverBumperException(f"Tag prefix '{self.tag}' does not match existing tag prefix '{prefix}'.")
            number = int(number) + 1
            tag = f"{prefix}{number}"

        else:
            tag = f"{tag}1"
        return major, minor, patch, tag
