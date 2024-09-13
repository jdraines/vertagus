import typing as T


class ManifestBase:
    manifest_type: str = "base"
    description: str = ""
    version: str
    loc: list[T.Union[str, int]] = []

    def __init__(self,
                 name: str,
                 path: str,
                 loc: list[T.Union[str, int]],
                 root: str = None
                 ):
        self.name = name
        self.path = path
        if loc:
            self.loc = loc
        self.root = root

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.path}, {self.loc}, {self.version})"
