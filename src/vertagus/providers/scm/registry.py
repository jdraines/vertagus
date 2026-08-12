from .git_ import GitScm
from vertagus.core.scm_base import ScmBase

_scm_types = {
    GitScm.scm_type: GitScm,
}


def get_scm_cls(scm_type: str) -> type[ScmBase]:
    if scm_type not in _scm_types:
        raise ValueError(f"Unknown scm type: {scm_type}")
    return _scm_types[scm_type]


def register_scm_cls(scm_cls: type[ScmBase]):
    _scm_types[scm_cls.scm_type] = scm_cls


def list_scm_types() -> list[str]:
    return sorted(list(_scm_types.keys()))
