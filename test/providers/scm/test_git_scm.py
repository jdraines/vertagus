from unittest.mock import patch, MagicMock

import pytest

from vertagus.providers.scm.git_ import git_scm as gscm



@pytest.fixture
def scm_config():
    return {
        "root": "/tmp",
        "remote_name": "test-remote"
    }

@pytest.fixture
def scm(scm_config, monkeypatch):
    monkeypatch.setattr(gscm, "git", MagicMock())
    return gscm.GitScm(**scm_config)


@pytest.fixture
def mock_tag():
    return gscm.Tag("1.0.0")


@pytest.fixture
def mock_alias():
    class MockAlias(gscm.AliasBase):
        def as_string(self, tag_prefix):
            return f"{tag_prefix}-alias"
    return  MockAlias("1.0.0")


def test_init(scm, scm_config):
    assert scm.root == scm_config["root"]
    assert scm.tag_prefix is None
    assert scm.remote_name == scm_config["remote_name"]


def test_create_tag(scm, mock_tag):
    scm.create_tag(mock_tag)
    scm._repo.create_tag.assert_called_once()
    scm._repo.git.push.assert_called_once()


def test_delete_tag(scm, mock_tag):
    scm.delete_tag(mock_tag)
    scm._repo.delete_tag.assert_called_once()
    scm._repo.git.execute.assert_called()


def test_list_tags(scm):
    scm.list_tags()
    scm._repo.git.execute.assert_called_once_with(["git", "ls-remote", "--tags", scm.remote_name])
    _tags = ["pre-1", "pre-2", "pro-3", "pro-4", ]
    scm._repo.git.execute.return_value = "\n".join(_tags)
    assert scm.list_tags(prefix="pre-") == ["pre-1", "pre-2"]
    scm.tag_prefix = "pro-"
    assert scm.list_tags() == ["pro-3", "pro-4"]


def test_migrate_alias(scm, mock_alias):
    scm.delete_tag = MagicMock()
    scm.create_tag = MagicMock()
    scm.migrate_alias(mock_alias)
    scm.delete_tag.assert_called_once()
    scm.create_tag.assert_called_once()


def test_get_highest_version(scm):
    scm.list_tags = MagicMock()
    scm.list_tags.return_value = ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "side-2.0.0", "side-3.0.0"]
    scm.tag_prefix = None
    assert scm.get_highest_version() == "1.3.0"


