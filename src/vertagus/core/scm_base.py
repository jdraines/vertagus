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
