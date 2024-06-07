from vertagus.core.manifest_base import ManifestBase
import json
import os.path

class JsonManifest(ManifestBase):
    manifest_type: str = "json"

    def __init__(self,
                 name: str,
                 path: str,
                 loc: list = None,
                 root: str = None
                 ):
        super().__init__(name, path, loc, root)
        self._doc = self._load_doc()

    @property
    def version(self):
        if not self.loc:
            raise ValueError(f"No loc provided for manifest {self.name!r}")
        p = self._doc
        for k in self.loc:
            p = p[k]
        return p

    def _load_doc(self):
        path = self.path
        if self.root:
            path = os.path.join(self.root, path)
        with open(self.path) as f:
            return json.load(f)
