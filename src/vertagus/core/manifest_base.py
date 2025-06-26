import typing as T


class ManifestBase:
    manifest_type: str = "base"
    description: str = ""
    version: str
    loc: T.Sequence[T.Union[str, int]] | None = []

    def __init__(self,
                 name: str,
                 path: str,
                 loc: T.Sequence[T.Union[str, int]] | None,
                 root: str | None = None
                 ):
        self.name = name
        self.path = path
        if loc:
            self.loc = loc
        self.root = root

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.path}, {self.loc}, {self.version})"
