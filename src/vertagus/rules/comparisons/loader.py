import typing as T
from . import rules
from vertagus.core.rule_bases import ComparisonRule


def load_rules():
    _rules = []
    for obj in dir(rules):
        if issubclass(getattr(rules, obj), ComparisonRule):
            if obj.name != "base":
                _rules.append(getattr(rules, obj))
    return _rules


def get_rules(rule_names) -> list[T.Type[ComparisonRule]]:
    rules = load_rules()
    rules_d = {rule.name: rule for rule in rules if rule.name in rule_names}
    return [rules_d[rule_name] for rule_name in rule_names]
