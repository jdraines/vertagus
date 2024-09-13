class Tag:

    def __init__(self, tag_text: str):
        self.tag_text = tag_text

    def as_string(self, prefix: str = None) -> str:
        if prefix:
            return prefix + self.tag_text
        return self.tag_text


class AliasBase(Tag):
    name: str = ""
    description: str = ""