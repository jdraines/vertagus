from .tag_base import Tag, AliasBase
import typing as T


class ScmBase:
    
    scm_type = "base"
    tag_prefix: T.Optional[str] = None

    def __init__(self,
                 root: str | None = None,
                 version_strategy: str | None = "tag",
                 target_branch: str | None = None,
                 manifest_path: str | None = None,
                 manifest_type: str | None = None,
                 manifest_loc: T.Optional[str] = None,
                 **kwargs
                 ):
        raise NotImplementedError()

    def create_tag(self, tag: Tag, ref: str | None = None):
        raise NotImplementedError()
    
    def delete_tag(self, tag_name: str, suppress_warnings: bool = False):
        raise NotImplementedError()

    def list_tags(self, prefix: str | None = None):
        raise NotImplementedError()

    def get_highest_version(self, prefix: str | None = None, branch: str | None = None) -> str | None:
        raise NotImplementedError()

    def migrate_alias(self, alias: AliasBase, ref: str | None = None, suppress_warnings: bool = True):
        raise NotImplementedError()

    def get_branch_manifest_version(self, branch: str, manifest_path: str, manifest_type: str) -> str | None:
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
