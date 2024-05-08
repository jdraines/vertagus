import typing as T
from . import library
from vertagus.core.tag_base import AliasBase


def load_rules() -> list[T.Type[AliasBase]]:
    _rules = []
    for objname in dir(library):
        maybeobj = getattr(library, objname)
        if isinstance(maybeobj, type) and issubclass(maybeobj, AliasBase):
            obj: AliasBase = maybeobj
            if obj.name and obj.name != "base":
                _rules.append(obj)
    return _rules


def get_aliases(alias_names) -> list[T.Type[AliasBase]]:
    aliases: list[T.Type[AliasBase]] = load_rules()
    alias_d = {alias.name: alias for alias in aliases if alias.name in alias_names}
    return [alias_d[alias_name] for alias_name in alias_names]
