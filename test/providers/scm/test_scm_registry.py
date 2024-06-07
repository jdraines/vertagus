import pytest
from unittest.mock import MagicMock, patch

from vertagus.providers.scm import registry as scm_registry


@patch('vertagus.providers.scm.registry._scm_types', {"test": "OK"})
def test_get_scm_cls():
    assert scm_registry.get_scm_cls("test") == "OK"
    with pytest.raises(ValueError):
        scm_registry.get_scm_cls("not_test")

@patch('vertagus.providers.scm.registry._scm_types', {})
def test_register_scm_cls():
    class MockScm:
        scm_type = "test"
    scm_registry.register_scm_cls(MockScm)
    assert scm_registry.get_scm_cls("test") == MockScm
