import pytest

from vertagus.core import scm_base as sb


def test_scm_base_is_abstract():
    with pytest.raises(NotImplementedError):
        sb.ScmBase(None)
        
    scm_base = sb.ScmBase.__new__(sb.ScmBase)

    with pytest.raises(NotImplementedError):    
        scm_base.create_tag("tag")
    
    with pytest.raises(NotImplementedError):
        scm_base.delete_tag("tag")

    with pytest.raises(NotImplementedError):
        scm_base.list_tags()

    with pytest.raises(NotImplementedError):
        scm_base.get_highest_version()

    with pytest.raises(NotImplementedError):
        scm_base.migrate_alias("alias")


def test_get_branch_manifest_version_not_implemented():
    """Test that get_branch_manifest_version raises NotImplementedError on base class."""
    # Create a mock SCM instance that bypasses __init__
    scm = sb.ScmBase.__new__(sb.ScmBase)
    
    with pytest.raises(NotImplementedError):
        scm.get_branch_manifest_version(
            branch="main",
            manifest_path="pyproject.toml",
            manifest_type="setuptools_pyproject"
        )


class MockScmWithBranchSupport(sb.ScmBase):
    """Mock SCM implementation with branch support for testing."""
    
    def __init__(self, root: str = "/test", version_strategy: str = "tag", 
                 target_branch=None, **kwargs):
        self.root = root
        self.version_strategy = version_strategy
        self.target_branch = target_branch
        self.kwargs = kwargs

    def create_tag(self, tag, ref=None):
        pass

    def delete_tag(self, tag_name, suppress_warnings=False):
        pass

    def list_tags(self, prefix=None):
        return []

    def get_highest_version(self, prefix=None):
        return "1.0.0"

    def migrate_alias(self, alias, ref=None, suppress_warnings=True):
        pass

    def get_branch_manifest_version(self, branch: str, manifest_path: str, 
                                  manifest_type: str):
        """Mock implementation that returns a test version."""
        if branch == "main" and manifest_path == "pyproject.toml":
            return "1.2.3"
        return None


def test_scm_initialization_with_branch_strategy():
    """Test SCM initialization with branch strategy parameters."""
    branch_scm = MockScmWithBranchSupport(
        root="/test/repo",
        version_strategy="branch",
        target_branch="main"
    )
    
    assert branch_scm.version_strategy == "branch"
    assert branch_scm.target_branch == "main"
    assert branch_scm.root == "/test/repo"


def test_scm_initialization_with_tag_strategy():
    """Test SCM initialization with tag strategy (default)."""
    tag_scm = MockScmWithBranchSupport(
        root="/test/repo",
        version_strategy="tag"
    )
    
    assert tag_scm.version_strategy == "tag"
    assert tag_scm.target_branch is None
    assert tag_scm.root == "/test/repo"


def test_get_branch_manifest_version_success():
    """Test successful retrieval of version from branch manifest."""
    branch_scm = MockScmWithBranchSupport(
        root="/test/repo",
        version_strategy="branch",
        target_branch="main"
    )
    
    version = branch_scm.get_branch_manifest_version(
        branch="main",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject"
    )
    
    assert version == "1.2.3"


def test_get_branch_manifest_version_not_found():
    """Test get_branch_manifest_version when version is not found."""
    branch_scm = MockScmWithBranchSupport(
        root="/test/repo",
        version_strategy="branch",
        target_branch="main"
    )
    
    version = branch_scm.get_branch_manifest_version(
        branch="nonexistent",
        manifest_path="pyproject.toml",
        manifest_type="setuptools_pyproject"
    )
    
    assert version is None


def test_branch_scm_has_required_attributes():
    """Test that branch SCM has all required attributes."""
    branch_scm = MockScmWithBranchSupport(
        root="/test/repo",
        version_strategy="branch",
        target_branch="main"
    )
    
    assert hasattr(branch_scm, 'version_strategy')
    assert hasattr(branch_scm, 'target_branch')
    assert hasattr(branch_scm, 'get_branch_manifest_version')

