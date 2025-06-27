import os
from logging import getLogger
from configparser import NoSectionError
from typing import cast, Optional

import git
from git.remote import Remote
from git.exc import GitCommandError
from git.objects import Commit
from packaging.version import parse as parse_version, InvalidVersion
from vertagus.core.scm_base import ScmBase
from vertagus.core.tag_base import Tag, AliasBase
from vertagus.providers.manifest.registry import get_manifest_cls


logger = getLogger(__name__)


class GitManifestNotFoundError(Exception):
    pass


class GitScm(ScmBase):

    scm_type = "git"
    _default_user_data = {
        "name": "vertagus",
        "email": "vertagus@none"
    }
    _default_remote_name = "origin"
    _default_version_strategy = "tag"

    def __init__(self,
                 root: Optional[str] = None,
                 tag_prefix: Optional[str] = None,
                 remote_name: Optional[str] = None,
                 version_strategy: Optional[str] = "tag",
                 target_branch: Optional[str] = None,
                 manifest_path: Optional[str] = None,
                 manifest_type: Optional[str] = None,
                 manifest_loc: Optional[list[str]] = None,
                 **kwargs
                 ):
        self.root = root or os.getcwd()
        self.tag_prefix = tag_prefix
        self.remote_name = remote_name or self._default_remote_name
        self.version_strategy = version_strategy or self._default_version_strategy
        self.target_branch = target_branch
        self.manifest_path = manifest_path
        self.manifest_type = manifest_type
        self.manifest_loc = manifest_loc
        self._repo = self._initialize_repo()

    @property
    def remote(self) -> Remote:
        return self._repo.remotes[self.remote_name]


    def create_tag(self, tag: Tag, ref: Optional[str] = None):
        tag_prefix = self.tag_prefix or ""
        tag_text = tag.as_string(tag_prefix)
        if ref:
            commit = self._repo.commit(ref)
        else:
            commit = self._repo.head.commit
        if isinstance(commit, Commit):
            commit = commit.hexsha
        logger.info(
            f"Creating tag {tag_text} at commit {commit}"
        )
        self._repo.create_tag(
            path=tag_text,
            ref=commit,
            message=tag_text,
        )
        self._repo.git.push(tags=True)
    
    def delete_tag(self, tag: Tag, suppress_warnings: bool=False):
        _tags = [t.name for t in self._repo.tags]
        logger.debug(
            f"Tags found: {_tags}"
        )
        tag_text = tag.as_string(self.tag_prefix)
        try:
            self._repo.delete_tag(tag_text)
        except GitCommandError as e:
            if not suppress_warnings:
                logger.warning(
                    f"Error encountered while deleting local tag {tag_text!r}: {e.__class__.__name__}: {e}"
                )
        try:
            self._repo.git.execute(["git", "push", "--delete", self.remote_name, tag_text])
        except GitCommandError as e:
            if not suppress_warnings:
                logger.warning(
                    f"Error encountered while deleting remote tag {tag_text!r}: {e.__class__.__name__}: {e}"
                )
        self._repo.git.push(tags=True)

    def list_tags(self, prefix: Optional[str] = None):

        def _ls_remote() -> str:
            return cast(
                str,
                self._repo.git.execute(
                        ["git", "ls-remote", "--tags", self.remote_name]
                    )
                )

        tags = [
            t.split("tags/")[-1].strip() for t in
            _ls_remote().split("\n")
            if not t.endswith("^{}")
        ]
        if not prefix and self.tag_prefix:
            prefix = self.tag_prefix
        if prefix:
            tags = [tag for tag in tags if tag.startswith(prefix)]
        return tags

    def migrate_alias(self,
                      alias: AliasBase,
                      ref: Optional[str] = None,
                      suppress_warnings: bool=True
                      ):
        logger.info(
            f"Migrating alias {alias.name} to ref {ref}"
        )
        try:
            self.delete_tag(alias, suppress_warnings=suppress_warnings)
        except GitCommandError as e:
            if not suppress_warnings:
                logger.warning(f"Error encountered while deleting alias {alias.name}: {e.__class__.__name__}: {e}")
        self.create_tag(alias, ref=ref)

    def get_highest_version(self,
                            prefix: Optional[str] = None,
                            branch: Optional[str] = None
                            ) -> Optional[str]:
        if self.version_strategy == 'branch':
            if not branch and not self.target_branch:
                raise ValueError("Branch-based strategy requires a target_branch to be configured or passed")
            if not self.manifest_path or not self.manifest_type:
                raise ValueError("Branch-based strategy requires manifest_path and manifest_type to be configured")

            branch = cast(str, branch or self.target_branch)

            manifest_path = self.manifest_path.lstrip('./')
            version = self.get_branch_manifest_version(
                branch=branch,
                manifest_path=manifest_path,
                manifest_type=self.manifest_type,
                manifest_loc=self.manifest_loc
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
    
    def _initialize_repo(self):
        repo = git.Repo(self.root)
        user_data = self._get_user_data(repo)
        logger.debug(
            f"Initializing git repository at {self.root} "
            f"with user data {user_data}."
        )
        repo.config_writer().set_value(
            "user", "name", user_data['name']
        ).release()
        repo.config_writer().set_value(
            "user", "email", user_data['email']
        ).release()
        return repo

    def _get_user_data(self, repo: git.Repo):
        try: 
            return {
                "name": repo.config_reader().get_value("user", "name"),
                "email": repo.config_reader().get_value("user", "email")
            }
        except NoSectionError:
            logger.warning("No user data found in git config. Setting default values.")
            return self._default_user_data

    def get_branch_manifest_version(self,
                                    branch: str,
                                    manifest_path: str,
                                    manifest_type: str,
                                    manifest_loc: Optional[list[str]] = None
                                    ) -> Optional[str]:
        """
        Get the version from a manifest file on a specific branch.
        """
        # Fetch the latest changes from remote
        self._repo.git.fetch(self.remote_name)
        # Get the content of the manifest file from the specified branch
        file_content = self._repo.git.show(f"{self.remote_name}/{branch}:{manifest_path}")
        if not file_content:
            raise GitManifestNotFoundError(f"Manifest file {manifest_path} not found on branch {branch}")
        
        manifest_cls = get_manifest_cls(manifest_type)
        return manifest_cls.version_from_content(
            content=file_content,
            name=manifest_path,
            loc=manifest_loc
        )
