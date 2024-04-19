from vertagus.core.project import Project
from vertagus.core.scm_base import ScmBase


def validate_project_version(scm: ScmBase,
                             project: Project,
                             stage_name: str = None
                             ) -> bool:
    previous_version = scm.get_highest_version()
    return project.validate_version(
        previous_version,
        stage_name
    )


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
    