import typing as T


class ManifestBase:
    manifest_type: str = "base"
    description: str = ""
    version: str
    loc: T.Optional[T.Sequence[T.Union[str, int]]] = []

    def __init__(self,
                 name: str,
                 path: str,
                 loc: T.Optional[T.Sequence[T.Union[str, int]]],
                 root: T.Optional[str] = None
                 ):
        self.name = name
        self.path = path
        if loc:
            self.loc = loc
        self.root = root

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.path}, {self.loc}, {self.version})"

    @classmethod
    def version_from_content(cls,
                             content: str,
                             name: str,
                             loc: T.Optional[T.Sequence[T.Union[str, int]]] = None,
                             ) -> str:
        """
        Retrieve the version from the content of the manifest file.
        """
        raise NotImplementedError("Subclasses must implement version_from_content method")


    @classmethod
    def _get_version(cls, doc, loc: T.Sequence[T.Union[str, int]], name: str) -> str:
        p = doc
        for k in loc:
            if k not in p:
                raise ValueError(
                    f"Invalid loc {loc!r} for manifest {name!r}. "
                    f"Key {k!r} not found in {list(p.keys())}"
                )
            p = p[k]
        return p

    def update_version(self, version: str, write: bool = True):
        raise NotImplementedError(
            "Method `update_version` is not implemented for Manifest of type "
            f"{self.__class__.__name__!r}."
        )
