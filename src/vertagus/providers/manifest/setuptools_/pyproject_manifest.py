from collections.abc import Sequence
from typing import cast

from ..toml_manifest import TomlManifest


class SetuptoolsPyprojectManifest(TomlManifest):
    manifest_type: str = "setuptools_pyproject"
    description: str = "A setuptools pyproject.toml file. Uses `project.version` as the version location."
    loc: Sequence[str | int] | None = ["project", "version"]

    def __init__(self, name: str, path: str, loc: list | None = None, root: str | None = None):
        super().__init__(name, path, loc, root)
        if loc:
            self.loc = loc
        self._doc = self._load_doc()

    @classmethod
    def version_from_content(
        cls,
        content: str,
        name: str,
        loc: list[str] | None = None,
    ) -> str:
        if loc is None:
            loc = cast(list[str], cls.loc)
        return super().version_from_content(content, name, loc)
