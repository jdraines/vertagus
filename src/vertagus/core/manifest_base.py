import typing as T


class ManifestBase:
    manifest_type: str = "base"

    def __init__(self,
                 name: str,
                 path: str,
                 loc: list[T.Union[str, int]],
                 version: str
                 ):
        self.name = name
        self.path = path
        self.loc = loc
        self.version = version

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.path}, {self.loc}, {self.version})"
