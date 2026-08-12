from unittest.mock import MagicMock, patch
from copy import copy
from datetime import datetime

import pytest

from vertagus.providers.scm.git_ import git_scm as gscm
from vertagus.providers.scm.git_.command import GitCommandError
from vertagus.providers.scm.git_.validation import GitValueError


@pytest.fixture
def scm_config():
    return {
        "root": "/tmp",
        "remote_name": "test-remote",
        "version_strategy": "tag",
    }

@pytest.fixture
def scm_config_with_branch_strategy():
    return {
        "root": "/tmp",
        "remote_name": "test-remote",
        "version_strategy": "branch",
        "target_branch": "main",
        "manifest_path": "path/to/manifest.yml",
        "manifest_type": "yaml",
        "manifest_loc": ["path/to/loc1", "path/to/loc2"],
    }

@pytest.fixture
def mock_git():
    """A stand-in for GitCommand whose run() returns an empty string."""
    git = MagicMock()
    git.run.return_value = ""
    return git

@pytest.fixture
def scm(scm_config, mock_git, monkeypatch):
    monkeypatch.setattr(gscm, "GitCommand", MagicMock(return_value=mock_git))
    return gscm.GitScm(**scm_config)

@pytest.fixture
def scm_with_branch_strategy(scm_config_with_branch_strategy, mock_git, monkeypatch):
    monkeypatch.setattr(gscm, "GitCommand", MagicMock(return_value=mock_git))
    return gscm.GitScm(**scm_config_with_branch_strategy)


@pytest.fixture
def mock_tag():
    return gscm.Tag("1.0.0")


@pytest.fixture
def mock_alias():
    class MockAlias(gscm.AliasBase):
        def as_string(self, tag_prefix):
            return f"{tag_prefix}alias"
    return  MockAlias("1.0.0")


def _run_calls(scm):
    """The positional argument vectors passed to GitCommand.run()."""
    return [call.args for call in scm._git.run.call_args_list]


def test_init(scm, scm_config):
    assert scm.root == scm_config["root"]
    assert scm.tag_prefix is None
    assert scm.remote_name == scm_config["remote_name"]


def test_create_tag(scm, mock_tag):
    scm._git.run.return_value = "abc123"
    scm.create_tag(mock_tag)
    calls = _run_calls(scm)
    assert ("tag", "-a", "-m", "1.0.0", "1.0.0", "abc123") in calls
    assert ("push", "--tags") in calls


def test_create_tag_passes_identity_without_writing_config(scm, mock_tag):
    """Identity is supplied per-invocation; the repo config is never written."""
    scm._git.run.return_value = "abc123"
    scm.create_tag(mock_tag)
    tag_call = next(c for c in scm._git.run.call_args_list if c.args[0] == "tag")
    assert set(tag_call.kwargs["config"]) == {"user.name", "user.email"}
    assert not any(c.args[:2] == ("config", "--replace-all") for c in scm._git.run.call_args_list)


def test_delete_tag(scm, mock_tag):
    scm.delete_tag(mock_tag)
    calls = _run_calls(scm)
    assert ("tag", "-d", "1.0.0") in calls
    assert ("push", "--delete", "test-remote", "1.0.0") in calls


def test_delete_tag_suppresses_warnings(scm, mock_tag, caplog):
    error = GitCommandError(["git", "tag", "-d", "1.0.0"], 1, "no such tag")
    scm._git.run.side_effect = [error, error, ""]
    scm.delete_tag(mock_tag, suppress_warnings=True)
    assert "Error encountered" not in caplog.text


def test_list_tags(scm):
    scm.list_tags()
    scm._git.run.assert_called_with("ls-remote", "--tags", scm.remote_name)
    _tags = ["pre-1", "pre-2", "pro-3", "pro-4", ]
    scm._git.run.return_value = "\n".join(_tags)
    assert scm.list_tags(prefix="pre-") == ["pre-1", "pre-2"]
    scm.tag_prefix = "pro-"
    assert scm.list_tags() == ["pro-3", "pro-4"]


def test_migrate_alias(scm, mock_alias):
    scm.delete_tag = MagicMock()
    scm.create_tag = MagicMock()
    scm.migrate_alias(mock_alias)
    scm.delete_tag.assert_called_once()
    scm.create_tag.assert_called_once()


def test_get_highest_version(scm, scm_with_branch_strategy):
    scm.list_tags = MagicMock()
    scm.list_tags.return_value = ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "side-2.0.0", "side-3.0.0"]
    scm.tag_prefix = None
    assert scm.get_highest_version() == "1.3.0"

    branch_scm = copy(scm_with_branch_strategy)
    branch_scm.get_branch_manifest_version = MagicMock(return_value="2.0.0")
    assert branch_scm.get_highest_version() == "2.0.0"

    branch_scm = copy(scm_with_branch_strategy)
    branch_scm.get_branch_manifest_version = MagicMock(return_value="2.0.0")
    branch_scm.target_branch = None
    assert branch_scm.get_highest_version(branch="main") == "2.0.0"

    with pytest.raises(ValueError):
        branch_scm = copy(scm_with_branch_strategy)
        branch_scm.get_branch_manifest_version = MagicMock(return_value="2.0.0")
        branch_scm.target_branch = None
        branch_scm.get_highest_version()

    with pytest.raises(ValueError):
        branch_scm = copy(scm_with_branch_strategy)
        branch_scm.get_branch_manifest_version = MagicMock(return_value="2.0.0")
        branch_scm.manifest_type = None
        branch_scm.get_highest_version()

    with pytest.raises(ValueError):
        branch_scm = copy(scm_with_branch_strategy)
        branch_scm.get_branch_manifest_version = MagicMock(return_value="2.0.0")
        branch_scm.manifest_path = None
        branch_scm.get_highest_version()


def test_get_branch_manifest_version(scm_with_branch_strategy):
    scm = scm_with_branch_strategy
    scm._git.run.return_value = "version: 1.2.3"
    with patch.object(gscm, "get_manifest_cls") as get_cls:
        get_cls.return_value.version_from_content.return_value = "1.2.3"
        assert scm.get_branch_manifest_version("main", "pyproject.toml", "yaml") == "1.2.3"
    calls = _run_calls(scm)
    assert ("fetch", "test-remote") in calls
    assert ("show", "test-remote/main:pyproject.toml") in calls


def test_get_branch_manifest_version_missing_file(scm_with_branch_strategy):
    scm = scm_with_branch_strategy
    scm._git.run.side_effect = [
        "",  # fetch
        GitCommandError(["git", "show"], 128, "does not exist"),
    ]
    with pytest.raises(gscm.GitManifestNotFoundError):
        scm.get_branch_manifest_version("main", "pyproject.toml", "yaml")


def test_get_commit_messages_since_highest_version(scm):
    scm.get_highest_version = MagicMock(return_value="1.0.0")
    scm._git.run.side_effect = [
        datetime(2025, 1, 1, 12, 0, 0).isoformat(),
        "Initial commit\n\x00Second commit\n\x00",
    ]
    messages = scm.get_commit_messages_since_highest_version()
    assert messages == ["Initial commit", "Second commit"]


def test_get_commit_messages_since_highest_version_missing_tag(scm):
    scm.get_highest_version = MagicMock(return_value="1.0.0")
    scm._git.run.side_effect = GitCommandError(["git", "log"], 128, "unknown revision")
    assert scm.get_commit_messages_since_highest_version() == []


# --- Argument injection regression tests -------------------------------------
#
# Every value below is attacker-reachable: the scm block of a vertagus config
# file, the `-b` CLI flag, or the version string parsed out of a manifest. A
# value in git option position is arbitrary command execution (--upload-pack) or
# arbitrary file write (--output), so each must be refused rather than forwarded.


@pytest.mark.parametrize(
    "field, value",
    [
        ("remote_name", "--upload-pack=touch /tmp/pwned"),
        ("remote_name", "origin\nfoo"),
        ("remote_name", "-o"),
        ("tag_prefix", "--output=/tmp/pwned"),
        ("tag_prefix", "v\n[core]\n\thooksPath=/tmp"),
        ("target_branch", "--output=/tmp/pwned"),
        ("manifest_path", "--output=/tmp/pwned"),
    ],
)
def test_option_like_config_values_are_rejected(scm_config, mock_git, monkeypatch, field, value):
    monkeypatch.setattr(gscm, "GitCommand", MagicMock(return_value=mock_git))
    config = {**scm_config, field: value}
    with pytest.raises(GitValueError):
        gscm.GitScm(**config)


def test_option_like_tag_text_is_rejected(scm, monkeypatch):
    """The version half of a tag comes from a manifest, so it is untrusted too."""
    scm.tag_prefix = None
    with pytest.raises(GitValueError):
        scm.create_tag(gscm.Tag("--output=/tmp/pwned"))
    assert not any(c.args[0] == "tag" for c in scm._git.run.call_args_list)


def test_option_like_branch_argument_is_rejected(scm_with_branch_strategy):
    with pytest.raises(GitValueError):
        scm_with_branch_strategy.get_highest_version(branch="--output=/tmp/pwned")


def test_option_like_ref_is_rejected(scm, mock_tag):
    with pytest.raises(GitValueError):
        scm.create_tag(mock_tag, ref="--output=/tmp/pwned")
