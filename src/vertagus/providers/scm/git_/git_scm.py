import os
from vertagus.core.scm_base import ScmBase
import git


class GitScm(ScmBase):

    scm_type = "git"

    def __init__(self, root: str):
        self.root = root or os.getcwd()
        self._repo = git.Repo(self.root)

    def create_tag(self, tag_name: str, commit_hash: str=None):
        if commit_hash:
            commit = self._repo.commit(commit_hash)
        else:
            commit = self._repo.head.commit
        self._repo.create_tag(
            path=tag_name,
            ref=commit,
            message=tag_name,
        )
    
    def delete_tag(self, tag_name: str):
        self._repo.delete_tag(tag_name)
    
    def list_tags(self, prefix: str=None):
        tags = self._repo.tags
        if prefix:
            tags = [tag for tag in tags if tag.name.startswith(prefix)]
        return tags
