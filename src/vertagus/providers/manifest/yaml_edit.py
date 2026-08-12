"""Edit a single scalar in a YAML document without disturbing the rest of it.

The counterpart to :mod:`vertagus.providers.manifest.toml_edit`, and written to the
same rule: locate the span of text holding a value and touch nothing else, or decline
by returning ``None`` so the caller can fall back to a full rewrite.

YAML is a far larger language than a version bump needs, so this models only the block
mappings that manifests are written in. Anchors, tags, flow collections, block scalars
and multiple documents are all recognized well enough to be refused rather than
misread.
"""

import typing as T

_WHITESPACE = " \t"


class _Unparseable(Exception):
    """Raised when the scanner meets YAML it does not model."""


class _Scalar(T.NamedTuple):
    path: tuple[str, ...]
    start: int
    end: int
    addressable: bool


def replace_value(text: str, path: T.Sequence[str], new_value: str) -> str | None:
    """Replace the scalar at ``path`` with ``new_value``, quoted as a YAML string.

    Returns the edited document, or ``None`` if the key could not be located
    unambiguously. Every byte outside the replaced scalar is preserved exactly.
    """
    if any(c in new_value for c in "\r\n") or any(c < " " for c in new_value):
        return None

    target = tuple(path)
    try:
        matches = [s for s in _iter_scalars(text) if s.path == target and s.addressable]
    except _Unparseable:
        return None
    if len(matches) != 1:
        return None

    match = matches[0]
    quoted = _quote_like(text[match.start : match.end], new_value)
    return text[: match.start] + quoted + text[match.end :]


def _quote_like(original: str, value: str) -> str:
    """Quote ``value`` in the style of the scalar it replaces, defaulting to single quotes.

    A version is always quoted, even where the original was plain: unquoted ``1.0`` is a
    float to a YAML parser, and a bump must not change a value's type.
    """
    if original.startswith('"'):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return "'" + value.replace("'", "''") + "'"


def _iter_scalars(text: str) -> T.Iterator[_Scalar]:
    """Yield every ``key: scalar`` assignment in the document, with its path.

    Keys nested inside a sequence are yielded as unaddressable: a vertagus ``loc`` names
    mapping keys only, so such a key is never a legitimate target and must not be matched
    by one that happens to share its name.
    """
    lines = text.splitlines(keepends=True)
    offset = 0
    stack: list[tuple[int, str]] = []
    sequence_indent: int | None = None
    seen_content = False
    index = 0

    while index < len(lines):
        line = lines[index]
        line_start = offset
        offset += len(line)
        index += 1

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("---") or stripped.startswith("..."):
            if seen_content:
                raise _Unparseable("Multiple documents are not modelled")
            continue

        content = line.rstrip("\r\n")
        indent = len(content) - len(content.lstrip(" "))
        if "\t" in content[:indent]:
            raise _Unparseable("Tab indentation is not modelled")
        seen_content = True

        while stack and stack[-1][0] >= indent:
            stack.pop()
        if sequence_indent is not None and indent <= sequence_indent:
            sequence_indent = None

        body = content[indent:]
        if body.startswith("-"):
            sequence_indent = indent if sequence_indent is None else min(sequence_indent, indent)
            continue

        key, key_end = _scan_key(body)
        path = tuple(k for _, k in stack) + (key,)
        value = body[key_end:]
        value_offset = key_end + len(value) - len(value.lstrip(_WHITESPACE))
        value = value.strip()

        if not value or value.startswith("#"):
            stack.append((indent, key))
            continue
        if value[0] in "&*!":
            raise _Unparseable("Anchors, aliases and tags are not modelled")
        if value[0] in "[{":
            raise _Unparseable("Flow collections are not modelled")
        if value[0] in "|>":
            index, offset = _skip_block_scalar(lines, index, offset, indent)
            continue

        start = line_start + indent + value_offset
        yield _Scalar(path, start, start + _scalar_length(content[indent + value_offset :]), sequence_indent is None)


def _scan_key(body: str) -> tuple[str, int]:
    """Scan a mapping key, returning it and the offset just past its colon."""
    if body[0] in ("'", '"'):
        end = _scan_quoted(body, 0)
        key = _unquote(body[:end])
        rest = end
    else:
        rest = _find_key_separator(body)
        key = body[:rest].rstrip(_WHITESPACE)
        if not key:
            raise _Unparseable("Empty mapping key")
        return key, rest + 1

    while rest < len(body) and body[rest] in _WHITESPACE:
        rest += 1
    if rest >= len(body) or body[rest] != ":":
        raise _Unparseable("Expected ':' after a quoted key")
    return key, rest + 1


def _find_key_separator(body: str) -> int:
    """Find the ``:`` that ends a plain key: one at the end of the line or followed by a space."""
    for i, char in enumerate(body):
        if char == "#" and i and body[i - 1] in _WHITESPACE:
            break
        if char == ":" and (i + 1 == len(body) or body[i + 1] in _WHITESPACE):
            return i
    raise _Unparseable(f"Not a mapping entry: {body!r}")


def _scalar_length(value: str) -> int:
    """Return the length of the scalar at the start of ``value``, excluding any comment."""
    if value[0] in ("'", '"'):
        return _scan_quoted(value, 0)
    end = len(value)
    for i, char in enumerate(value):
        if char == "#" and i and value[i - 1] in _WHITESPACE:
            end = i
            break
    return len(value[:end].rstrip(_WHITESPACE))


def _scan_quoted(text: str, index: int) -> int:
    """Scan a quoted scalar, returning the offset just past its closing quote."""
    quote = text[index]
    index += 1
    while index < len(text):
        char = text[index]
        if quote == '"' and char == "\\":
            index += 2
            continue
        if char == quote:
            if quote == "'" and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            return index + 1
        index += 1
    raise _Unparseable("Unterminated quoted scalar")


def _unquote(text: str) -> str:
    """Return the value of a quoted scalar."""
    if text.startswith("'"):
        return text[1:-1].replace("''", "'")
    return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")


def _skip_block_scalar(lines: list[str], index: int, offset: int, indent: int) -> tuple[int, int]:
    """Skip the body of a ``|`` or ``>`` block scalar, which is indented past its key."""
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped:
            content = line.rstrip("\r\n")
            if len(content) - len(content.lstrip(" ")) <= indent:
                break
        offset += len(line)
        index += 1
    return index, offset
