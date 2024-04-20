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
    if not result:
        logger.error(
            f"Version for current version {current_version} validation failed: "
            f"previous version: {previous_version}"
        )
    else:
        logger.info(f"Validated: current version {current_version}")
    return result


def create_tags(scm: ScmBase,
                project: Project,
                stage_name: str = None,
                ref: str = None
                ) -> None:
    version = project.get_version()
    scm.create_tag(version, ref=ref)
    if stage_name:
        aliases = project.get_aliases(stage_name, scm.tag_prefix)
        for alias in aliases:
            scm.create_tag(alias, ref=ref)
    