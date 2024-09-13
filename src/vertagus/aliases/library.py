from vertagus.core.tag_base import AliasBase


class StringAlias(AliasBase):
    name = ""
    alias_value = ""
    use_prefix = False

    def as_string(self, prefix: str = None) -> str:
        prefix = prefix or ""
        if self.use_prefix:
            return prefix + self.alias_value
        return self.alias_value


class StableAlias(StringAlias):
    name = "string:stable"
    alias_value = "stable"
    description = "A simple alias, 'stable'. Prefix will be ignored even if present in config."


class LatestAlias(StringAlias):
    name = "string:latest"
    alias_value ="latest"
    description = "A simple alias, 'latest'. Prefix will be ignored even if present in config."


class StablePrefixedAlias(StringAlias):
    name = "string:prefixed:stable"
    alias_value ="stable"
    use_prefix = True
    description = "A prefixed alias, '<prefix>-stable'."

class LatestPrefixedAlias(StringAlias):
    name = "string:prefixed:latest"
    alias_value ="latest"
    use_prefix = True
    description = "A prefixed alias, '<prefix>-latest'."

class MajorMinor(AliasBase):
    name = "major.minor"
    description = "A version alias that only includes the major and minor parts of the version."

    def as_string(self, prefix: str = None) -> str:
        prefix = prefix or ""
        parts = self.tag_text.split(".")
        if len(parts) < 2:
            raise ValueError(
                f"Version must have at least two parts. Found version "
                f"{self.tag_text}"
            )
        return prefix + ".".join(parts[:2])
