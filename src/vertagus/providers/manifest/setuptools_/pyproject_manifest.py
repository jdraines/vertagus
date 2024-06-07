from vertagus.core.manifest_base import ManifestBase
from ..toml_manifest import TomlManifest


class SetuptoolsPyprojectManifest(TomlManifest):
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
