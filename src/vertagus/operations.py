from logging import getLogger

from vertagus.core.project import Project
from vertagus.core.scm_base import ScmBase


logger = getLogger(__name__)


def validate_project_version(scm: ScmBase,
                             project: Project,
                             stage_name: str = None
                             ) -> bool:
    previous_version = scm.get_highest_version()
    result = project.validate_version(
        previous_version,
        stage_name
    )
    current_version = project.get_version()
    if result:
        logger.info(f"Successfully validated current version: {current_version}")
    return result


def create_tags(scm: ScmBase,
                project: Project,
                stage_name: str = None,
                ref: str = None
                ) -> None:
    logger.info(f"Creating tags for project {project.name}, stage {stage_name}")
    version = project.get_version()
    scm.create_tag(version, ref=ref)
    if stage_name:
        aliases = project.get_aliases(stage_name, scm.tag_prefix)
        for alias in aliases:
            logger.info(
                f"Creating tag {alias} for project {project.name}, stage {stage_name}"
            )
            scm.create_tag(alias, ref=ref)
    