from vertagus.core.manifest_base import ManifestBase
from . import toml_edit
import tomllib
import tomli_w
import os.path
from logging import getLogger


logger = getLogger(__name__)


class TomlManifest(ManifestBase):
    manifest_type: str = "toml"
    description: str = "A TOML file. Users provide a custom `loc` to the version as a list of keys."

    def __init__(self, name: str, path: str, loc: list = None, root: str = None):
        super().__init__(name, path, loc, root)
        self._doc = self._load_doc()

    @property
    def version(self):
        if not self.loc:
            raise ValueError(f"No loc provided for manifest {self.name!r}")
        return self._get_version(self._doc, self.loc, self.name)

    def _load_doc(self):
        path = self._full_path()
        with open(path, "rb") as f:
            return tomllib.load(f)

    def _full_path(self):
        path = self.path
        if self.root:
            path = os.path.join(self.root, path)
        return path

    def _write_doc(self):
        """Rewrite the whole document from the parsed data, losing comments and formatting."""
        path = self._full_path()
        with open(path, "wb") as f:
            tomli_w.dump(self._doc, f)

    def _write_version_in_place(self, version: str) -> bool:
        """Rewrite just the version in the file on disk, leaving the rest of it untouched.

        Returns False when the version could not be located and replaced safely, so that
        the caller can fall back to rewriting the whole document.
        """
        path = self._full_path()
        with open(path, encoding="utf-8", newline="") as f:
            original = f.read()

        edited = toml_edit.replace_value(original, self.loc, version)
        if edited is None or not self._edit_is_faithful(original, edited, version):
            return False

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(edited)
        return True

    def _edit_is_faithful(self, original: str, edited: str, version: str) -> bool:
        """Whether an edited document parses to the original data with only the version changed."""
        try:
            edited_doc = tomllib.loads(edited)
            expected_doc = tomllib.loads(original)
        except tomllib.TOMLDecodeError:
            return False
        p = expected_doc
        for k in self.loc[:-1]:
            p = p[k]
        p[self.loc[-1]] = version
        return edited_doc == expected_doc

    @classmethod
    def version_from_content(
        cls,
        content: str,
        name: str,
        loc: list[str] | None = None,
    ) -> str:
        if loc is None:
            raise ValueError("loc must be provided for TomlManifest")
        manifest_content = tomllib.loads(content)
        return cls._get_version(manifest_content, loc, name)

    def update_version(self, version: str, write: bool = True):
        if not self.loc:
            raise ValueError(f"No loc provided for manifest {self.name!r}")
        p = self._doc
        for k in self.loc[:-1]:
            if k not in p:
                raise ValueError(
                    f"Invalid loc {self.loc!r} for manifest {self.name!r}. Key {k!r} not found in {list(p.keys())}"
                )
            p = p[k]
        p[self.loc[-1]] = version
        if write:
            if not self._write_version_in_place(version):
                logger.warning(
                    f"Could not update the version in place in {self._full_path()}; rewriting the whole "
                    "file. Comments and formatting in this file may not be preserved."
                )
                self._write_doc()
