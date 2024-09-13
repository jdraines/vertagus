from vertagus.core.manifest_base import ManifestBase
import yaml
import os.path

class YamlManifest(ManifestBase):
    manifest_type: str = "yaml"
    description: str = "A YAML file. Users provide a custom `loc` to the version as a list of keys."

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
            if k not in p:
                raise ValueError(
                    f"Invalid loc {self.loc!r} for manifest {self.name!r}. "
                    f"Key {k!r} not found in {list(p.keys())}"
                )
            p = p[k]
        return p

    def _load_doc(self):
        path = self._full_path()
        with open(path) as f:
            return yaml.safe_load(f)

    def _full_path(self):
        path = self.path
        if self.root:
            path = os.path.join(self.root, path)
        return path
