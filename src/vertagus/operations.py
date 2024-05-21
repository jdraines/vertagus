from logging import getLogger

from vertagus.core.project import Project
from vertagus.core.tag_base import Tag, AliasBase
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
