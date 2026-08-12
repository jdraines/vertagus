"""Tests for the validators guarding the git command line.

Every value these check originates in a configuration file, a CLI flag, or a
manifest, none of which are trusted when vertagus runs in CI.
"""

import pytest

from vertagus.errors import ConfigurationError
from vertagus.providers.scm.git_.command import GitCommand
from vertagus.providers.scm.git_.validation import (
    GitValueError,
    validate_config_key,
    validate_config_value,
    validate_ref_name,
    validate_remote_name,
)


def test_git_value_error_is_reported_as_a_configuration_error():
    """The CLI prints ConfigurationError without a traceback, so these must be one."""
    assert issubclass(GitValueError, ConfigurationError)


@pytest.mark.parametrize(
    "value",
    [
        "--upload-pack=id",
        "ref with space",
        "ref~1",
        "ref^1",
        "ref:name",
        "ref?",
        "ref*",
        "ref[a]",
        "ref\\name",
        "a..b",
        "/leading",
        "trailing/",
        "double//slash",
        "trailing.",
        "@",
        "ref\nname",
        "",
    ],
)
def test_validate_ref_name_rejects(value):
    with pytest.raises(GitValueError):
        validate_ref_name(value)


@pytest.mark.parametrize(
    "value",
    [
        "main@{upstream}",  # reflog/upstream syntax resolves to a different ref
        "refs/.hidden",  # a component may not begin with '.'
        ".hidden",
        "foo.lock",  # nor end with '.lock'
        "foo.lock/bar",
        "refs/heads/x.lock",
    ],
)
def test_validate_ref_name_rejects_what_check_ref_format_rejects(value):
    """These are refused by `git check-ref-format` per slash-separated component."""
    with pytest.raises(GitValueError):
        validate_ref_name(value)


@pytest.mark.parametrize(
    "value",
    ["main", "v1.2.3", "refs/heads/main", "release/1.0", "feature/a-b_c", "HEAD"],
)
def test_validate_ref_name_accepts_ordinary_refs(value):
    assert validate_ref_name(value) == value


@pytest.mark.parametrize("value", ["origin", "upstream", "my-remote", "r2.d2", "a_b"])
def test_validate_remote_name_accepts(value):
    assert validate_remote_name(value) == value


@pytest.mark.parametrize(
    "value",
    ["", "-o", "--upload-pack=id", "origin\nfoo", "has space", "git@host:repo.git", ".leading"],
)
def test_validate_remote_name_rejects(value):
    with pytest.raises(GitValueError):
        validate_remote_name(value)


@pytest.mark.parametrize(
    "key",
    [
        # git splits `-c` on the first '=', so a key carrying one reassigns a
        # different setting than the caller intended -- both of these run commands.
        "user.name=x\ncore.hooksPath",
        "core.sshCommand=touch /tmp/pwned",
        "user.name\ncore.hooksPath",
        "",
        "-c",
        "1user.name",
    ],
)
def test_validate_config_key_rejects(key):
    with pytest.raises(GitValueError):
        validate_config_key(key)


@pytest.mark.parametrize("key", ["user.name", "user.email", "core.hooksPath", "a-b_c.d"])
def test_validate_config_key_accepts(key):
    assert validate_config_key(key) == key


def test_validate_config_value_rejects_newlines():
    with pytest.raises(GitValueError):
        validate_config_value("me\n[core]\n\thooksPath=/tmp", "user.name")


def test_git_command_rejects_an_option_bearing_config_key(tmp_path):
    with pytest.raises(GitValueError):
        GitCommand(str(tmp_path), config={"core.sshCommand=touch /tmp/pwned": "x"})


def test_git_command_rejects_an_option_bearing_config_key_per_invocation(tmp_path):
    git = GitCommand(str(tmp_path))
    with pytest.raises(GitValueError):
        git.run("status", config={"user.name=y\ncore.hooksPath": "x"})
