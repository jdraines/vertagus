class AliasBase:
    name: str = ""

    @classmethod
    def create_alias(self, version: str, alias_prefix: str = None) -> str:
        raise NotImplementedError()
