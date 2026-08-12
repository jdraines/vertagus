import os
from datetime import datetime, timedelta
from logging import getLogger
from typing import ClassVar

from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from vertagus.core.scm_base import ScmBase
from vertagus.core.tag_base import AliasBase, Tag
from vertagus.providers.manifest.registry import get_manifest_cls

from .command import GitCommand, GitCommandError
from .validation import (
    validate_path,
    validate_ref_name,
    validate_remote_name,
    validate_rev,
    validate_tag_prefix,
)

logger = getLogger(__name__)


class GitManifestNotFoundError(Exception):
    pass


class GitScm(ScmBase):
    scm_type = "git"
    _default_user_data: ClassVar[dict[str, str]] = {"name": "vertagus", "email": "vertagus@none"}
    _default_remote_name = "origin"
    _default_version_strategy = "tag"

    def __init__(
        self,
        root: str | None = None,
        tag_prefix: str | None = None,
        remote_name: str | None = None,
        version_strategy: str | None = "tag",
        target_branch: str | None = None,
        manifest_path: str | None = None,
        manifest_type: str | None = None,
        manifest_loc: list[str] | None = None,
        **kwargs,
    ):
        self.root = root or os.getcwd()
        self.tag_prefix = validate_tag_prefix(tag_prefix) if tag_prefix else tag_prefix
        self.remote_name = validate_remote_name(remote_name or self._default_remote_name)
        self.version_strategy = version_strategy or self._default_version_strategy
        self.target_branch = validate_ref_name(target_branch, "target_branch") if target_branch else target_branch
        self.manifest_path = validate_path(manifest_path, "manifest_path") if manifest_path else manifest_path
        self.manifest_type = manifest_type
        self.manifest_loc = manifest_loc
        self._git = self._initialize_repo()

    def create_tag(self, tag: Tag, ref: str | None = None):
        tag_text = self._tag_text(tag)
        commit = self._resolve_commit(ref) if ref else self._resolve_commit("HEAD")
        logger.info(f"Creating tag {tag_text} at commit {commit}")
        self._git.run("tag", "-a", "-m", tag_text, tag_text, commit, config=self._identity_config())
        self._git.run("push", "--tags")

    def delete_tag(self, tag: Tag, suppress_warnings: bool = False):
        tag_text = self._tag_text(tag)
        try:
            self._git.run("tag", "-d", tag_text)
        except GitCommandError as e:
            if not suppress_warnings:
                logger.warning(f"Error encountered while deleting local tag {tag_text!r}: {e.__class__.__name__}: {e}")
        try:
            self._git.run("push", "--delete", self.remote_name, tag_text)
        except GitCommandError as e:
            if not suppress_warnings:
                logger.warning(f"Error encountered while deleting remote tag {tag_text!r}: {e.__class__.__name__}: {e}")
        self._git.run("push", "--tags")

    def list_tags(self, prefix: str | None = None):
        output = self._git.run("ls-remote", "--tags", self.remote_name)
        tags = [t.split("tags/")[-1].strip() for t in output.split("\n") if not t.endswith("^{}")]
        if not prefix and self.tag_prefix:
            prefix = self.tag_prefix
        if prefix:
            tags = [tag for tag in tags if tag.startswith(prefix)]
        return tags

    def migrate_alias(self, alias: AliasBase, ref: str | None = None, suppress_warnings: bool = True):
        logger.info(f"Migrating alias {alias.name} to ref {ref}")
        try:
            self.delete_tag(alias, suppress_warnings=suppress_warnings)
        except GitCommandError as e:
            if not suppress_warnings:
                logger.warning(f"Error encountered while deleting alias {alias.name}: {e.__class__.__name__}: {e}")
        self.create_tag(alias, ref=ref)

    def get_highest_version(self, prefix: str | None = None, branch: str | None = None) -> str | None:
        if self.version_strategy == "branch":
            if not branch and not self.target_branch:
                raise ValueError("Branch-based strategy requires a target_branch to be configured or passed")
            if not self.manifest_path or not self.manifest_type:
                raise ValueError("Branch-based strategy requires manifest_path and manifest_type to be configured")

            branch = validate_ref_name(branch or self.target_branch, "branch")  # type: ignore[arg-type]

            manifest_path = self.manifest_path.lstrip("./")
            version = self.get_branch_manifest_version(
                branch=branch,
                manifest_path=manifest_path,
                manifest_type=self.manifest_type,
                manifest_loc=self.manifest_loc,
            )

            if version is None:
                logger.error(f"Could not retrieve version from branch '{self.target_branch}'")
            return version
        else:
            # Original tag-based strategy
            if not prefix and self.tag_prefix:
                prefix = self.tag_prefix
            tags = self.list_tags(prefix=prefix)
            if not tags:
                return None
            versions = tags
            if prefix:
                versions = [tag.replace(prefix, "") for tag in tags]

            valid_versions = []
            for version in versions:
                try:
                    parse_version(version)
                    valid_versions.append(version)
                except InvalidVersion:
                    logger.warning(f"Invalid version found: {version}")
            if not valid_versions:
                return None
            return max(valid_versions, key=lambda v: parse_version(v))

    def _initialize_repo(self) -> GitCommand:
        git = GitCommand(self.root)
        logger.debug(f"Using git repository at {self.root}.")
        git.run("rev-parse", "--git-dir")
        return git

    def _identity_config(self) -> dict[str, str]:
        """The committer identity to use for commands that write objects.

        Passed per-invocation with ``-c`` rather than written into the
        repository's config, so that vertagus never modifies a repository it was
        only asked to read.
        """
        name = self._git.run("config", "--get", "user.name", check=False)
        email = self._git.run("config", "--get", "user.email", check=False)
        if not name or not email:
            logger.warning("No user data found in git config. Using default values.")
        return {
            "user.name": name or self._default_user_data["name"],
            "user.email": email or self._default_user_data["email"],
        }

    def _tag_text(self, tag: Tag) -> str:
        """Render a tag to its full text and validate it as a refname.

        The version half of this string comes from a manifest, so it is no more
        trusted than the configured prefix.
        """
        return validate_ref_name(tag.as_string(self.tag_prefix or ""), "tag")

    def _resolve_commit(self, ref: str) -> str:
        """Resolve a revision to a commit sha."""
        rev = validate_rev(ref)
        return self._git.run("rev-parse", "--verify", f"{rev}^{{commit}}")

    def get_branch_manifest_version(
        self, branch: str, manifest_path: str, manifest_type: str, manifest_loc: list[str] | None = None
    ) -> str | None:
        """
        Get the version from a manifest file on a specific branch.
        """
        branch = validate_ref_name(branch, "branch")
        manifest_path = validate_path(manifest_path, "manifest_path")
        # Fetch the latest changes from remote
        self._git.run("fetch", self.remote_name)
        # Get the content of the manifest file from the specified branch
        try:
            file_content = self._git.run("show", f"{self.remote_name}/{branch}:{manifest_path}")
        except GitCommandError as e:
            raise GitManifestNotFoundError(f"Manifest file {manifest_path} not found on branch {branch}: {e}") from e
        if not file_content:
            raise GitManifestNotFoundError(f"Manifest file {manifest_path} not found on branch {branch}")

        manifest_cls = get_manifest_cls(manifest_type)
        return manifest_cls.version_from_content(content=file_content, name=manifest_path, loc=manifest_loc)

    def get_commit_messages_since_highest_version(self, branch: str | None = None) -> list[str]:
        """
        Get commit messages since the highest version tag.
        """
        highest_version = self.get_highest_version(prefix=self.tag_prefix if self.tag_prefix else None, branch=branch)
        if not highest_version:
            logger.warning("No tags found to compare against.")
            return []

        tag_name = validate_ref_name(
            f"{self.tag_prefix}{highest_version}" if self.tag_prefix else highest_version, "tag"
        )
        try:
            tagged_commit_date = datetime.fromisoformat(self._git.run("log", "-1", "--format=%cI", tag_name))
        except (ValueError, GitCommandError):
            logger.error(f"Tag {tag_name} not found.")
            return []
        since = (tagged_commit_date + timedelta(seconds=1)).isoformat()
        # The revision goes last and is the only one: `--branches=<name>` would
        # not do this job, because git implies a trailing '/*' on a pattern with
        # no glob character, so `--branches=main` matches refs/heads/main/* and
        # silently selects nothing.
        rev = validate_rev(branch, "branch") if branch else "HEAD"
        output = self._git.run("log", f"--since={since}", "--format=%B%x00", rev)
        return [message.strip() for message in output.split("\x00") if message.strip()]
