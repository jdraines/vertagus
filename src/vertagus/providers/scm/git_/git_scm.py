import os
import git
from git.exc import GitCommandError
from packaging import version
from vertagus.core.scm_base import ScmBase

class GitScm(ScmBase):

    scm_type = "git"

    def __init__(self, root: str = None, tag_prefix: str = None):
        self.root = root or os.getcwd()
        self.tag_prefix = tag_prefix
        self._repo = git.Repo(self.root)

    def create_tag(self, tag_name: str, ref: str=None):
        if self.tag_prefix:
            tag_name = f"{self.tag_prefix}{tag_name}"
        if ref:
            commit = self._repo.commit(ref)
        else:
            commit = self._repo.head.commit
        self._repo.create_tag(
            path=tag_name,
            ref=commit,
            message=tag_name,
        )
    
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