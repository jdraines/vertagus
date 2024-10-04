from .tag_base import Tag
import typing as T


class ScmBase:
    
    scm_tpe = "base"
    tag_prefix: T.Optional[str] = None

    def __init__(self, root: str, **kwargs):
        raise NotImplementedError()

    def create_tag(self, tag: Tag, ref: str=None):
        raise NotImplementedError()
    
    def delete_tag(self, tag_name: str, suppress_warnings: bool=False):
        raise NotImplementedError()
    
    def list_tags(self, prefix: str=None):
        raise NotImplementedError()

    def get_highest_version(self, prefix: str=None):
        raise NotImplementedError()

    def migrate_alias(self, alias: str, ref: str = None, suppress_warnings: bool=True):
        raise NotImplementedError()
