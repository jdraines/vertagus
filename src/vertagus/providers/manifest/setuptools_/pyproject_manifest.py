from vertagus.core.manifest_base import ManifestBase
import tomli
import os.path

class SetuptoolsPyprojectManifest(ManifestBase):
    manifest_type: str = "setuptools_pyproject"
    loc = ["project", "version"]

    def __init__(self,
                 name: str,
                 path: str,
                 loc: list = None,
                 root: str = None
                 ):
        super().__init__(name, path, loc, root)
        if loc:
            self.loc = loc
        self._doc = self._load_doc()

    @property
    def version(self):
        p = self._doc
        for k in self.loc:
            p = p[k]
        return p

    def _load_doc(self):
        path = self.path
        if self.root:
            path = os.path.join(self.root, path)
        with open(self.path, 'rb') as f:
            return tomli.load(f)
