import os
from logging import getLogger

import git
from git.exc import GitCommandError
from packaging import version
from vertagus.core.scm_base import ScmBase
from vertagus.core.tag_base import Tag


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
        # self._repo.create_tag(
        #     path=tag_name,
        #     ref=commit,
        #     message=tag_name,
        # )
    
    def delete_tag(self, tag_name: str):
        if self.tag_prefix:
            tag_name = f"{self.tag_prefix}{tag_name}"
        self._repo.delete_tag(tag_name)
    
    def list_tags(self, prefix: str=None):
        tags = self._repo.tags
        if not prefix and self.tag_prefix:
            prefix = self.tag_prefix
        if prefix:
            tags = [tag for tag in tags if tag.name.startswith(prefix)]
        return tags

    def migrate_alias(self, alias: str, ref: str = None):
        if self.tag_prefix:
            alias = f"{self.tag_prefix}{alias}"
        try:
            self._repo.delete_tag(alias)
        except GitCommandError:
            pass
        
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
