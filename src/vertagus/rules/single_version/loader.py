import typing as T
from . import library
from vertagus.core.rule_bases import SingleVersionRule


def load_rules() -> list[T.Type[SingleVersionRule]]:
    _rules = []
    for objname in dir(library):
        maybeobj = getattr(library, objname)
        if isinstance(maybeobj, type) and issubclass(maybeobj, SingleVersionRule):
            obj: T.Type[SingleVersionRule] = maybeobj
            if obj.name != "base":
                _rules.append(obj)
    return _rules


def get_rules(rule_names=None) -> list[T.Type[SingleVersionRule]]:
    rules: list[T.Type[SingleVersionRule]] = load_rules()
    if rule_names is None:
        rule_names = [rule.name for rule in rules]
    not_found = set(rule_names) - {rule.name for rule in rules}
    if not_found:
        raise ValueError(f"Rules not found: {not_found}")
    rules_d = {rule.name: rule for rule in rules if rule.name in rule_names}
    return [rules_d[rule_name] for rule_name in rule_names]
