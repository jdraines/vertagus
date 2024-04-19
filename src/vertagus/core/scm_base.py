import typing as T


class ScmBase:
    
    scm_tpe = "base"
    tag_prefix: T.Optional[str] = None

    def __init__(self, **kwargs):
        raise NotImplementedError()

    def create_tag(self, tag_name: str, ref: str=None):
        raise NotImplementedError()
    
    def delete_tag(self, tag_name: str):
        raise NotImplementedError()
    
    def list_tags(self, prefix: str=None):
        raise NotImplementedError()

    def get_highest_version(self, prefix: str=None):
        raise NotImplementedError()

    def migrate_alias(self, alias: str, ref: str = None):
        raise NotImplementedError()
