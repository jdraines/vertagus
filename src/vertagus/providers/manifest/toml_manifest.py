from vertagus.core.manifest_base import ManifestBase
import tomli
import tomli_w
import os.path
from typing import Optional


class TomlManifest(ManifestBase):
    manifest_type: str = "toml"
    description: str = "A TOML file. Users provide a custom `loc` to the version as a list of keys."

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
        return self._get_version(self._doc, self.loc, self.name)

    def _load_doc(self):
        path = self._full_path()
        with open(path, 'rb') as f:
            return tomli.load(f)

    def _full_path(self):
        path = self.path
        if self.root:
            path = os.path.join(self.root, path)
        return path

    def _write_doc(self):
        path = self._full_path()
        with open(path, 'wb') as f:
            tomli_w.dump(self._doc, f)

    @classmethod
    def version_from_content(cls,
                             content: str,
                             name: str,
                             loc: Optional[list[str]] = None,
                             ) -> str:
        if loc is None:
            raise ValueError("loc must be provided for TomlManifest")
        manifest_content = tomli.loads(content)
        return cls._get_version(manifest_content, loc, name)

    def update_version(self, version: str, write: bool = True):
        if not self.loc:
            raise ValueError(f"No loc provided for manifest {self.name!r}")
        p = self._doc
        for k in self.loc[:-1]:
            if k not in p:
                raise ValueError(
                    f"Invalid loc {self.loc!r} for manifest {self.name!r}. "
                    f"Key {k!r} not found in {list(p.keys())}"
                )
            p = p[k]
        p[self.loc[-1]] = version
        if write:
            self._write_doc()
