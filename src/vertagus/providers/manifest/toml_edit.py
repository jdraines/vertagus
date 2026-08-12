"""Edit a single value in a TOML document without disturbing the rest of it.

Serializing a parsed TOML document back to text loses everything the parser threw
away: comments, blank lines, key order, and the author's choice of quoting and
indentation. That is an unacceptable trade for a version bump, which changes a
handful of characters, so vertagus rewrites the version in place instead.

The scanner here understands just enough TOML to find the span of text holding a
value: table headers, dotted keys, and the string, array and inline-table forms a
value can take. Anything it does not recognize makes it give up and return
``None`` rather than guess, which lets the caller fall back to a full rewrite.
"""

import typing as T

_BARE_KEY_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-")
_WHITESPACE = " \t"


class _Unparseable(Exception):
    """Raised when the scanner meets TOML it does not model."""


class _KeyValue(T.NamedTuple):
    path: tuple[str, ...]
    value_start: int
    value_end: int


def replace_value(text: str, path: T.Sequence[str], new_value: str) -> str | None:
    """Replace the value at ``path`` with ``new_value``, quoted as a TOML basic string.

    Returns the edited document, or ``None`` if the key could not be located
    unambiguously. Every byte outside the replaced value is preserved exactly.
    """
    target = tuple(path)
    try:
        matches = [kv for kv in _iter_key_values(text) if kv.path == target]
    except _Unparseable:
        return None
    if len(matches) != 1:
        return None

    match = matches[0]
    return text[: match.value_start] + _format_basic_string(new_value) + text[match.value_end :]


def _format_basic_string(value: str) -> str:
    """Render a string as a TOML basic string."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    for char, escape in (("\b", "\\b"), ("\t", "\\t"), ("\n", "\\n"), ("\f", "\\f"), ("\r", "\\r")):
        escaped = escaped.replace(char, escape)
    escaped = "".join(c if c >= " " and c != "\x7f" else f"\\u{ord(c):04x}" for c in escaped)
    return f'"{escaped}"'


def _iter_key_values(text: str) -> T.Iterator[_KeyValue]:
    """Yield every key/value assignment in the document, with its fully qualified path.

    Keys inside arrays of tables are yielded under a path that cannot be addressed by
    a vertagus ``loc`` (which names dict keys only), so they can never be matched.
    """
    index = 0
    length = len(text)
    table: tuple[str, ...] = ()
    in_array_of_tables = False

    while index < length:
        char = text[index]
        if char in _WHITESPACE or char in "\r\n":
            index += 1
            continue
        if char == "#":
            index = _skip_to_end_of_line(text, index)
            continue
        if char == "[":
            table, in_array_of_tables, index = _scan_table_header(text, index)
            continue

        path, value_start, value_end, index = _scan_key_value(text, index)
        if not in_array_of_tables:
            yield _KeyValue(table + path, value_start, value_end)


def _scan_table_header(text: str, index: int) -> tuple[tuple[str, ...], bool, int]:
    """Scan a ``[table]`` or ``[[array.of.tables]]`` header."""
    is_array_of_tables = text.startswith("[[", index)
    index += 2 if is_array_of_tables else 1
    path, index = _scan_key_path(text, index)
    index = _skip_whitespace(text, index)
    closing = "]]" if is_array_of_tables else "]"
    if not text.startswith(closing, index):
        raise _Unparseable(f"Unterminated table header at offset {index}")
    return path, is_array_of_tables, index + len(closing)


def _scan_key_value(text: str, index: int) -> tuple[tuple[str, ...], int, int, int]:
    """Scan a ``key = value`` assignment, returning the key path and the value's span."""
    path, index = _scan_key_path(text, index)
    index = _skip_whitespace(text, index)
    if index >= len(text) or text[index] != "=":
        raise _Unparseable(f"Expected '=' after key at offset {index}")
    index = _skip_whitespace(text, index + 1)
    value_start = index
    value_end = _scan_value(text, index)
    return path, value_start, value_end, value_end


def _scan_key_path(text: str, index: int) -> tuple[tuple[str, ...], int]:
    """Scan a possibly dotted key, whose parts may be bare or quoted."""
    parts: list[str] = []
    while True:
        index = _skip_whitespace(text, index)
        if index >= len(text):
            raise _Unparseable("Document ended inside a key")
        char = text[index]
        if char in ("'", '"'):
            end = _scan_quoted_string(text, index)
            parts.append(text[index + 1 : end - 1])
            index = end
        else:
            start = index
            while index < len(text) and text[index] in _BARE_KEY_CHARS:
                index += 1
            if index == start:
                raise _Unparseable(f"Expected a key at offset {index}")
            parts.append(text[start:index])
        index = _skip_whitespace(text, index)
        if index < len(text) and text[index] == ".":
            index += 1
            continue
        return tuple(parts), index


def _scan_value(text: str, index: int) -> int:
    """Return the offset just past the value beginning at ``index``."""
    if index >= len(text):
        raise _Unparseable("Document ended where a value was expected")
    char = text[index]
    if char in ("'", '"'):
        return _scan_quoted_string(text, index)
    if char == "[":
        return _scan_bracketed(text, index, "[", "]")
    if char == "{":
        return _scan_bracketed(text, index, "{", "}")
    return _scan_bare_value(text, index)


def _scan_quoted_string(text: str, index: int) -> int:
    """Scan a basic, literal, or multi-line string, returning the offset past its close."""
    quote = text[index]
    if text.startswith(quote * 3, index):
        delimiter = quote * 3
        escapes = quote == '"'
        index += 3
    else:
        delimiter = quote
        escapes = quote == '"'
        index += 1

    while index < len(text):
        char = text[index]
        if escapes and char == "\\":
            index += 2
            continue
        if text.startswith(delimiter, index):
            index += len(delimiter)
            # A multi-line string may end with up to two extra quote characters.
            if len(delimiter) == 3:
                extra = 0
                while extra < 2 and index < len(text) and text[index] == quote:
                    index += 1
                    extra += 1
            return index
        if len(delimiter) == 1 and char in "\r\n":
            raise _Unparseable(f"Unterminated string at offset {index}")
        index += 1
    raise _Unparseable("Document ended inside a string")


def _scan_bracketed(text: str, index: int, opening: str, closing: str) -> int:
    """Scan an array or inline table, skipping over nested values, strings and comments."""
    depth = 0
    while index < len(text):
        char = text[index]
        if char in ("'", '"'):
            index = _scan_quoted_string(text, index)
            continue
        if char == "#":
            index = _skip_to_end_of_line(text, index)
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise _Unparseable(f"Unterminated {opening!r} at offset {index}")


def _scan_bare_value(text: str, index: int) -> int:
    """Scan a number, boolean or date, which runs to a comment or the end of the line."""
    end = index
    while end < len(text) and text[end] not in "\r\n#":
        end += 1
    value = text[index:end]
    trimmed = value.rstrip(_WHITESPACE)
    if not trimmed:
        raise _Unparseable(f"Empty value at offset {index}")
    return index + len(trimmed)


def _skip_whitespace(text: str, index: int) -> int:
    while index < len(text) and text[index] in _WHITESPACE:
        index += 1
    return index


def _skip_to_end_of_line(text: str, index: int) -> int:
    while index < len(text) and text[index] not in "\r\n":
        index += 1
    return index
