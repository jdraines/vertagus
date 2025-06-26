from .tag_base import Tag, AliasBase
import typing as T


class ScmBase:
    
    scm_type = "base"
    tag_prefix: T.Optional[str] = None

    def __init__(self,
                 root: T.Optional[str] = None,
                 version_strategy: T.Optional[str] = "tag",
                 target_branch: T.Optional[str] = None,
                 manifest_path: T.Optional[str] = None,
                 manifest_type: T.Optional[str] = None,
                 manifest_loc: T.Optional[str] = None,
                 **kwargs
                 ):
        raise NotImplementedError()

    def create_tag(self, tag: Tag, ref: T.Optional[str] = None):
        raise NotImplementedError()
    
    def delete_tag(self, tag_name: str, suppress_warnings: bool = False):
        raise NotImplementedError()

    def list_tags(self, prefix: T.Optional[str] = None):
        raise NotImplementedError()

    def get_highest_version(self, prefix: T.Optional[str] = None, branch: T.Optional[str] = None) -> T.Optional[str]:
        raise NotImplementedError()

    def migrate_alias(self, alias: AliasBase, ref: T.Optional[str] = None, suppress_warnings: bool = True):
        raise NotImplementedError()

    def get_branch_manifest_version(self, branch: str, manifest_path: str, manifest_type: str) -> T.Optional[str]:
        """
        Get the version from a manifest file on a specific branch.
        
        Args:
            branch: The branch name to check
            manifest_path: Path to the manifest file relative to repo root
            manifest_type: Type of manifest (e.g., 'setuptools_pyproject')
        
        Returns:
            The version string from the manifest, or None if not found
        """
        raise NotImplementedError()
