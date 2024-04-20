import typing as T
from .git_ import GitScm


_scm_types = {
    GitScm.scm_type: GitScm,
}


def get_scm_cls(scm_type: str) -> T.Type[GitScm]:
    if scm_type not in _scm_types:
        raise ValueError(f"Unknown scm type: {scm_type}")
    return _scm_types[scm_type]


def register_scm_cls(scm_cls: T.Type[GitScm]):
    _scm_types[scm_cls.scm_type] = scm_cls
