import typing as T


class ManifestBase:
    manifest_type: str = "base"
    name: str
    path: str
    loc: list[T.Union[str, int]]
    version: str
