import os
from logging import getLogger

import git
from git.exc import GitCommandError
from packaging import version
from vertagus.core.scm_base import ScmBase
from vertagus.core.tag_base import Tag, AliasBase


logger = getLogger(__name__)


class GitScm(ScmBase):

    scm_type = "git"
    _default_user_data = {
        "name": "vertagus",
        "email": "vertagus@example.com"
    }

    def __init__(self, root: str = None, tag_prefix: str = None, user_data: dict = None):
        self.root = root or os.getcwd()
        self.tag_prefix = tag_prefix
        self.user_data = user_data or self._default_user_data
        self._repo = self._initialize_repo()

    def create_tag(self, tag: Tag, ref: str=None):
        tag_prefix = self.tag_prefix or ""
        tag_text = tag.as_string(tag_prefix)
        if ref:
            commit = self._repo.commit(ref)
        else:
            commit = self._repo.head.commit
        logger.info(
            f"Creating tag {tag_text} at commit {commit}"
        )
        self._repo.create_tag(
            path=tag_text,
            ref=commit,
            message=tag_text,
        )
        self._repo.git.push(tags=True)
    
    def delete_tag(self, tag: Tag):
        tag_text = tag.as_string(self.tag_prefix)
        self._repo.delete_tag(tag_text)
        self._repo.git.push(tags=True)
    
    def list_tags(self, prefix: str=None):
        tags = self._repo.tags
        if not prefix and self.tag_prefix:
            prefix = self.tag_prefix
        if prefix:
            tags = [tag for tag in tags if tag.name.startswith(prefix)]
        return tags

    def migrate_alias(self, alias: AliasBase, ref: str = None):
        logger.info(
            f"Migrating alias {alias.name} to ref {ref}"
        )
        try:
            self._repo.delete_tag(alias)
        except GitCommandError as e:
            logger.error(f"Error encountered while deleting alias {alias.name}: {e.__class__.__name__}: {e}")
        self.create_tag(alias, ref=ref)

    def get_highest_version(self, prefix: str = None):
        if not prefix and self.tag_prefix:
            prefix = self.tag_prefix
        tags = self.list_tags(prefix=prefix)
        if not tags:
            return None
        versions = tags
        if prefix:
            versions = [tag.replace(prefix, "") for tag in tags]
        return max(versions, key=lambda v: version.parse(v))
    
    def _initialize_repo(self):
        repo = git.Repo(self.root)
        logger.info(
            f"Initializing git repository at {self.root} "
            f"with user data {self.user_data}."
        )
        repo.config_writer().set_value(
            "user", "name", self.user_data['name']
        ).release()
        repo.config_writer().set_value(
            "user", "email", self.user_data['email']
        ).release()
        return repo
