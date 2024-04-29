import pytest

from vertagus.core import scm_base as sb


def test_scm_base_is_abstract():
    with pytest.raises(NotImplementedError):
        sb.ScmBase()
        
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
        
