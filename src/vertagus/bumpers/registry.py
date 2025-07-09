from typing import Type
from ..core.bumper_base import BumperBase
from .semantic import SemanticBumper


_bumpers = {
    SemanticBumper.name: SemanticBumper
}


def register_bumper(bumper_class: Type[BumperBase]) -> Type[BumperBase]:
    """
    Register a bumper class in the global registry.
    """
    if bumper_class.name in _bumpers:
        raise ValueError(f"Bumper with name '{bumper_class.name}' is already registered.")
    
    _bumpers[bumper_class.name] = bumper_class
    return bumper_class


def get_bumper_cls(bumper_name: str) -> Type[BumperBase]:
    if bumper_name not in _bumpers:
        raise ValueError(f"Bumper not found: {bumper_name}")
    return _bumpers[bumper_name]


def list_bumpers() -> list[str]:
    """
    List all registered bumpers.
    """
    return list(_bumpers.keys())
