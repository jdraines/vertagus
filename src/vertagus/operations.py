from logging import getLogger

from vertagus.core.project import Project
from vertagus.core.tag_base import Tag, AliasBase
from vertagus.core.scm_base import ScmBase


logger = getLogger(__name__)


def validate_project_version(scm: ScmBase,
                             project: Project,
                             stage_name: str = None
                             ) -> bool:
    # Check if we're using branch-based or tag-based strategy
    version_strategy = getattr(scm, 'version_strategy', 'tag')
    
    if version_strategy == 'branch':
        # Branch-based validation
        target_branch = getattr(scm, 'target_branch', None)
        if not target_branch:
            logger.error("Branch-based strategy requires a target_branch to be configured")
            return False
            
        # Get the version from the target branch
        manifests = project._get_manifests()  # Use the getter method
        if not manifests:
            logger.error("No manifests found in project")
            return False
        manifest = manifests[0]  # Use first manifest
        # Clean the manifest path (remove ./ prefix if present)
        manifest_path = manifest.path.lstrip('./')
        previous_version = scm.get_branch_manifest_version(
            branch=target_branch,
            manifest_path=manifest_path,
            manifest_type=manifest.manifest_type
        )
        
        if previous_version is None:
            logger.warning(f"Could not retrieve version from branch '{target_branch}'")
            # Optionally treat this as valid if no version exists on target branch
            previous_version = "0.0.0"
    else:
        # Tag-based validation (existing behavior)
        previous_version = scm.get_highest_version()
    
    result = project.validate_version(
        previous_version,
        stage_name
    )
    current_version = project.get_version()
    
    if result:
        logger.info(f"Successfully validated current version: {current_version} against previous version: {previous_version}")
    else:
        logger.error(f"Failed to validate current version: {current_version} against previous version: {previous_version}")
    
    return result


def create_tags(scm: ScmBase,
                project: Project,
                stage_name: str = None,
                ref: str = None
                ) -> None:
    tag = Tag(project.get_version())
    scm.create_tag(tag, ref=ref)
    aliases = project.get_aliases(stage_name)
    for alias in aliases:
        scm.migrate_alias(alias, ref=ref)


def create_aliases(scm: ScmBase,
                   project: Project,
                   stage_name: str = None,
                   ref: str = None
                   ) -> None:
    aliases = project.get_aliases(stage_name)
    for alias in aliases:
        scm.migrate_alias(alias, ref=ref)
