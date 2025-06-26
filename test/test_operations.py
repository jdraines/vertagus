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
        mock_logger.info.assert_called_once_with("Successfully validated current version: v1.0.1 against previous version: v1.0.0")
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


def test_validate_project_version_with_branch_scm():
    """Test project validation using branch-based SCM."""
    mock_branch_scm = Mock(spec=ScmBase)
    mock_branch_scm.version_strategy = "branch"
    mock_branch_scm.target_branch = "main"
    mock_branch_scm.get_highest_version.return_value = "1.1.0"
    
    mock_project = Mock(spec=Project)
    mock_project.validate_version.return_value = True
    mock_project.get_version.return_value = "1.1.0"
    
    with patch('vertagus.operations.logger') as mock_logger:
        result = validate_project_version(
            scm=mock_branch_scm,
            project=mock_project,
            stage_name="prod"
        )
        
        assert result is True
        mock_branch_scm.get_highest_version.assert_called_once()
        mock_project.validate_version.assert_called_once_with("1.1.0", "prod")
        mock_logger.info.assert_called_once_with("Successfully validated current version: 1.1.0 against previous version: 1.1.0")


def test_validate_project_version_with_tag_scm():
    """Test project validation using traditional tag-based SCM."""
    mock_tag_scm = Mock(spec=ScmBase)
    mock_tag_scm.version_strategy = "tag"
    mock_tag_scm.target_branch = None
    mock_tag_scm.get_highest_version.return_value = "1.0.0"
    
    mock_project = Mock(spec=Project)
    mock_project.validate_version.return_value = True
    mock_project.get_version.return_value = "1.1.0"
    
    with patch('vertagus.operations.logger') as mock_logger:
        result = validate_project_version(
            scm=mock_tag_scm,
            project=mock_project,
            stage_name="prod"
        )
        
        assert result is True
        mock_tag_scm.get_highest_version.assert_called_once()
        mock_project.validate_version.assert_called_once_with("1.0.0", "prod")
        mock_logger.info.assert_called_once_with("Successfully validated current version: 1.1.0 against previous version: 1.0.0")


def test_validate_project_version_branch_failure():
    """Test project validation failure with branch SCM."""
    mock_branch_scm = Mock(spec=ScmBase)
    mock_branch_scm.version_strategy = "branch"
    mock_branch_scm.target_branch = "main"
    mock_branch_scm.get_highest_version.return_value = "1.1.0"
    
    mock_project = Mock(spec=Project)
    mock_project.validate_version.return_value = False
    mock_project.get_version.return_value = "1.1.0"
    
    with patch('vertagus.operations.logger') as mock_logger:
        result = validate_project_version(
            scm=mock_branch_scm,
            project=mock_project
        )
        
        assert result is False
        mock_branch_scm.get_highest_version.assert_called_once()
        mock_project.validate_version.assert_called_once()
        mock_logger.error.assert_called_once_with("Failed to validate current version: 1.1.0 against previous version: 1.1.0")


def test_create_tags_with_branch_scm():
    """Test tag creation with branch-based SCM."""
    mock_branch_scm = Mock(spec=ScmBase)
    mock_branch_scm.version_strategy = "branch"
    mock_branch_scm.target_branch = "main"
    
    mock_project = Mock(spec=Project)
    mock_project.get_version.return_value = "1.1.0"
    mock_project.get_aliases.return_value = []
    
    with patch('vertagus.operations.Tag') as mock_tag_class:
        mock_tag = Mock()
        mock_tag_class.return_value = mock_tag
        
        create_tags(
            scm=mock_branch_scm,
            project=mock_project,
            stage_name="prod",
            ref="abc123"
        )
        
        mock_tag_class.assert_called_once_with("1.1.0")
        mock_branch_scm.create_tag.assert_called_once_with(mock_tag, ref="abc123")
        mock_project.get_aliases.assert_called_once_with("prod")


def test_branch_scm_has_required_attributes():
    """Test that branch SCM has the expected attributes."""
    mock_branch_scm = Mock(spec=ScmBase)
    mock_branch_scm.version_strategy = "branch"
    mock_branch_scm.target_branch = "main"
    mock_branch_scm.get_branch_manifest_version.return_value = "1.1.0"
    
    assert hasattr(mock_branch_scm, 'version_strategy')
    assert hasattr(mock_branch_scm, 'target_branch')
    assert mock_branch_scm.version_strategy == "branch"
    assert mock_branch_scm.target_branch == "main"
    
    # Test the get_branch_manifest_version method
    assert hasattr(mock_branch_scm, 'get_branch_manifest_version')
    
    version = mock_branch_scm.get_branch_manifest_version(
        branch="main",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject"
    )
    
    assert version == "1.1.0"
