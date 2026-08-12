"""Validation of values that reach a ``git`` command line.

Every value vertagus hands to ``git`` originates in either the configuration
file, a CLI flag, or the contents of a manifest -- none of which are trusted.
A value that lands in option position (anything beginning with ``-``) lets a
caller forge options such as ``--upload-pack`` or ``--output``, which is
equivalent to arbitrary command execution or arbitrary file write. Using an
argument vector rather than a shell does not help with that on its own, so the
values are validated here before they are ever passed along.
"""

import re

from vertagus.errors import ConfigurationError


class GitValueError(ConfigurationError):
    """Raised when a value destined for a git command line is unsafe.

    A :class:`~vertagus.errors.ConfigurationError` because every value checked
    here originates in a configuration file, a CLI flag, or a manifest -- so the
    CLI reports the message as user-facing guidance rather than a traceback.
    """


# Control characters, including NUL and newline. Newlines matter because git
# config values and refnames are line-oriented.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

_REMOTE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

_CONFIG_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")


def _reject_control_chars(value: str, field: str) -> None:
    match = _CONTROL_CHARS.search(value)
    if match:
        raise GitValueError(f"{field} may not contain control characters (found {match.group()!r} in {value!r}).")


def _reject_option_like(value: str, field: str) -> None:
    if value.startswith("-"):
        raise GitValueError(
            f"{field} may not begin with '-' (got {value!r}); such a value would be read by git as an option."
        )


def validate_remote_name(value: str) -> str:
    """Validate a git remote name.

    Remote names are the narrowest case -- git itself only accepts a restricted
    character set -- so this is a whitelist rather than a denylist.
    """
    if not value:
        raise GitValueError("remote_name may not be empty.")
    if not _REMOTE_NAME.match(value):
        raise GitValueError(
            f"remote_name {value!r} is not a valid git remote name. Expected letters, digits, '.', '_' or '-', "
            "beginning with a letter or digit."
        )
    return value


def validate_ref_name(value: str, field: str = "ref") -> str:
    """Validate a value used as a git refname (a tag or branch name).

    The rules mirror ``git check-ref-format``, so a value that passes here is one
    git will accept, without shelling out to ask.
    """
    if not value:
        raise GitValueError(f"{field} may not be empty.")
    _reject_control_chars(value, field)
    _reject_option_like(value, field)
    for forbidden in (" ", "~", "^", ":", "?", "*", "[", "\\", "..", "@{"):
        if forbidden in value:
            raise GitValueError(f"{field} may not contain {forbidden!r} (got {value!r}).")
    if value.startswith("/") or value.endswith("/") or "//" in value:
        raise GitValueError(f"{field} may not begin or end with '/', or contain '//' (got {value!r}).")
    if value.endswith("."):
        raise GitValueError(f"{field} may not end with '.' (got {value!r}).")
    if value == "@":
        raise GitValueError(f"{field} may not be '@'.")
    # git applies these per slash-separated component, not just to the whole
    # refname: refs/.hidden and foo.lock/bar are both rejected.
    for component in value.split("/"):
        if component.startswith("."):
            raise GitValueError(f"{field} may not have a path component beginning with '.' (got {value!r}).")
        if component.endswith(".lock"):
            raise GitValueError(f"{field} may not have a path component ending with '.lock' (got {value!r}).")
    return value


def validate_rev(value: str, field: str = "ref") -> str:
    """Validate a value used as a git revision.

    Looser than :func:`validate_ref_name` because a revision may legitimately be
    a hex sha, ``HEAD``, or an expression such as ``origin/main`` or ``v1^{}``.
    The security-relevant properties -- no option position, no control
    characters -- still hold.
    """
    if not value:
        raise GitValueError(f"{field} may not be empty.")
    _reject_control_chars(value, field)
    _reject_option_like(value, field)
    return value


def validate_path(value: str, field: str = "path") -> str:
    """Validate a repository-relative path handed to git."""
    if not value:
        raise GitValueError(f"{field} may not be empty.")
    _reject_control_chars(value, field)
    _reject_option_like(value, field)
    return value


def validate_tag_prefix(value: str, field: str = "tag_prefix") -> str:
    """Validate a tag prefix.

    A prefix is not a refname on its own -- it is concatenated with a version --
    so it is checked for the properties that survive concatenation. The full tag
    text is validated as a refname separately at the point of use.
    """
    _reject_control_chars(value, field)
    _reject_option_like(value, field)
    return value


def validate_config_key(key: str) -> str:
    """Validate a key passed to git as ``-c <key>=<value>``.

    git splits ``-c`` on the first ``=``, so a key containing one silently
    reassigns the setting the caller thought they were writing -- ``core.hooksPath``
    and ``core.sshCommand`` both run commands. A whitelist is workable here
    because every key vertagus sets is a plain ``section.name`` pair.
    """
    if not key:
        raise GitValueError("git config key may not be empty.")
    if not _CONFIG_KEY.match(key):
        raise GitValueError(
            f"git config key {key!r} is not a valid key. Expected letters, digits, '.', '_' or '-', "
            "beginning with a letter."
        )
    return key


def validate_config_value(value: str, field: str) -> str:
    """Validate a value passed to git as ``-c <key>=<value>``.

    A newline here would let a caller append unrelated directives such as
    ``core.sshCommand`` or ``core.hooksPath``, both of which run commands.
    """
    _reject_control_chars(value, field)
    return value
