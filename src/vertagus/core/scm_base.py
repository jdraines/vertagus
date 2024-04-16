class ScmBase:
    
    scm_tpe = "base"

    def create_tag(self, tag_name: str, commit_hash: str=None):
        raise NotImplementedError()
    
    def delete_tag(self, tag_name: str):
        raise NotImplementedError()
    
    def list_tags(self, prefix: str=None):
        raise NotImplementedError()
