from vertagus.core.alias_base import AliasBase


class StringAlias(AliasBase):
    name = ""
    value = ""
    use_prefix = False

    @classmethod
    def create_alias(cls, version: str, alias_prefix: str = None) -> str:
        alias_prefix = alias_prefix or ""
        if cls.use_prefix:
            return alias_prefix + cls.value
        return cls.value


class StableAlias(StringAlias):
    name = "string:stable"
    value = "stable"


class LatestAlias(StringAlias):
    name = "string:latest"
    value = "latest"


class StablePrefixedAlias(StringAlias):
    name = "string:prefixed:stable"
    value = "stable"
    use_prefix = True


class LatestPrefixedAlias(StringAlias):
    name = "string:prefixed:latest"
    value = "latest"
    use_prefix = True


class MajorMinor(AliasBase):
    name = "major.minor"

    @classmethod
    def create_alias(cls, version: str, alias_prefix: str = None) -> str:
        alias_prefix = alias_prefix or ""
        parts = version.split(".")
        if len(parts) < 2:
            raise ValueError("Version must have at least two parts")
        return alias_prefix + ".".join(parts[:2])
