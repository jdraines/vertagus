"""Integration tests that drive real git repositories.

The unit tests for GitScm mock the command layer, which means they verify the
argument vectors but not that git accepts them. These run the real thing against
throwaway repositories in tmp_path.
"""

import os
import shutil
import subprocess

import pytest

from vertagus.core.tag_base import Tag
from vertagus.providers.scm.git_.command import GitCommand, GitCommandError
from vertagus.providers.scm.git_.git_scm import GitScm
from vertagus.providers.scm.git_.validation import GitValueError


pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")


def _git(cwd, *args, date=None):
    env = None
    if date:
        env = {**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env)


@pytest.fixture
def upstream(tmp_path):
    """A bare repository standing in for a remote."""
    path = tmp_path / "upstream.git"
    path.mkdir()
    _git(path, "init", "--bare", "-b", "main")
    return path


@pytest.fixture
def repo(tmp_path, upstream):
    path = tmp_path / "repo"
    path.mkdir()
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.name", "tester")
    _git(path, "config", "user.email", "tester@example.com")
    (path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "1.2.3"\n')
    _git(path, "add", ".")
    _git(path, "commit", "-m", "initial commit", date="2025-01-01T12:00:00+00:00")
    _git(path, "remote", "add", "origin", str(upstream))
    _git(path, "push", "-u", "origin", "main")
    return path


def test_create_and_list_tags(repo):
    scm = GitScm(root=str(repo), tag_prefix="v")
    scm.create_tag(Tag("1.2.3"))
    assert scm.list_tags() == ["v1.2.3"]
    assert scm.get_highest_version() == "1.2.3"


def test_delete_tag(repo):
    scm = GitScm(root=str(repo), tag_prefix="v")
    scm.create_tag(Tag("1.2.3"))
    scm.delete_tag(Tag("1.2.3"))
    assert scm.list_tags() == []


def test_create_tag_does_not_write_repo_config(repo):
    """A repo with no identity configured is left untouched by vertagus."""
    _git(repo, "config", "--unset", "user.name")
    _git(repo, "config", "--unset", "user.email")
    before = (repo / ".git" / "config").read_text()
    scm = GitScm(root=str(repo), tag_prefix="v")
    scm.create_tag(Tag("1.2.3"))
    assert (repo / ".git" / "config").read_text() == before
    assert scm.list_tags() == ["v1.2.3"]


def test_get_branch_manifest_version(repo):
    scm = GitScm(
        root=str(repo),
        version_strategy="branch",
        target_branch="main",
        manifest_path="./pyproject.toml",
        manifest_type="setuptools_pyproject",
    )
    assert scm.get_highest_version() == "1.2.3"


def test_get_commit_messages_since_highest_version(repo):
    scm = GitScm(root=str(repo), tag_prefix="v")
    scm.create_tag(Tag("1.2.3"))
    (repo / "file.txt").write_text("hello")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "a second commit", date="2025-01-01T13:00:00+00:00")
    messages = scm.get_commit_messages_since_highest_version()
    assert "a second commit" in messages
    assert "initial commit" not in messages


def test_upload_pack_injection_does_not_execute(repo, tmp_path):
    """The PoC from the security review, end to end.

    Before this change, `remote_name` reached `git fetch` in option position and
    `--upload-pack` ran an arbitrary command.
    """
    canary = tmp_path / "PWNED"
    payload = f"--upload-pack=touch {canary}; git-upload-pack"
    with pytest.raises(GitValueError):
        GitScm(
            root=str(repo),
            remote_name=payload,
            version_strategy="branch",
            target_branch="main",
            manifest_path="./pyproject.toml",
            manifest_type="setuptools_pyproject",
        )
    assert not canary.exists()


def test_command_reports_failures(repo):
    git = GitCommand(str(repo))
    with pytest.raises(GitCommandError) as excinfo:
        git.run("rev-parse", "--verify", "refs/tags/nope")
    assert excinfo.value.returncode != 0


def test_command_does_not_use_a_shell(repo, tmp_path):
    canary = tmp_path / "SHELL_RAN"
    git = GitCommand(str(repo))
    git.run("tag", "-a", "-m", "msg", f"weird;touch{canary}", "HEAD", check=False)
    assert not canary.exists()
