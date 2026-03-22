import typing as T
from vertagus.core.rule_bases import Rule, SingleVersionRule, ComparisonRule
from vertagus.rules.single_version.loader import load_rules as load_sv_rules
from vertagus.rules.comparison.loader import load_rules as load_comp_rules


def get_all_rules() -> dict[str, type[Rule]]:
    """Load all rules from both libraries into a unified name->class map."""
    registry: dict[str, type[Rule]] = {}
    for rule_cls in load_sv_rules():
        registry[rule_cls.name] = rule_cls
    for rule_cls in load_comp_rules():
        registry[rule_cls.name] = rule_cls
    return registry


def get_rule(name: str) -> type[Rule]:
    """Look up a single rule by name."""
    registry = get_all_rules()
    if name not in registry:
        raise ValueError(f"Rule not found: {name!r}")
    return registry[name]


def get_rule_category(rule_cls: type[Rule]) -> str:
    """Returns 'single_version' or 'comparison'."""
    if issubclass(rule_cls, SingleVersionRule):
        return "single_version"
    elif issubclass(rule_cls, ComparisonRule):
        return "comparison"
    raise ValueError(f"Unknown rule category for: {rule_cls}")
