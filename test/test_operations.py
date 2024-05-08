import pytest
from unittest.mock import Mock, patch
from vertagus.operations import validate_project_version, create_tags
from vertagus.core.project import Project
from vertagus.core.scm_base import ScmBase
from vertagus.core.tag_base import Tag


def test_validate_project_version():
    mock_scm = Mock(spec=ScmBase)
    mock_scm.get_highest_version.return_value = 'v1.0.0'
 
    mock_project = Mock(spec=Project)
    mock_project.validate_version.return_value = True
    mock_project.get_version.return_value = 'v1.0.1'
 
    with patch('vertagus.operations.logger') as mock_logger:
        result = validate_project_version(mock_scm, mock_project, 'stage1')
        mock_logger.info.assert_called_once_with("Successfully validated current version: v1.0.1")
    assert result is True


def test_create_tags_normal():
    mock_scm = Mock(spec=ScmBase)
    mock_project = Mock(spec=Project)
    mock_project.get_version.return_value = 'v1.0.1'
    mock_project.get_aliases.return_value = ['alias1', 'alias2']
    mock_scm.create_tag.return_value = None
    mock_scm.migrate_alias.return_value = None

    create_tags(mock_scm, mock_project, 'stage1', 'ref1')

    mock_scm.create_tag.assert_called_once()
    mock_scm.migrate_alias.assert_any_call('alias1', ref='ref1')
    mock_scm.migrate_alias.assert_any_call('alias2', ref='ref1')


def test_create_tags_no_stage():
    mock_scm = Mock(spec=ScmBase)
    mock_project = Mock(spec=Project)
    mock_project.get_version.return_value = 'v1.0.1'
    mock_project.get_aliases.return_value = []  
    mock_scm.create_tag.return_value = None
    create_tags(mock_scm, mock_project, ref='ref1')
    mock_scm.create_tag.assert_called_once()
    mock_scm.migrate_alias.assert_not_called()
