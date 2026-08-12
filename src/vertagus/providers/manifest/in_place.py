"""Shared machinery for updating a manifest's version without rewriting the whole file."""

import typing as T
from logging import getLogger


logger = getLogger(__name__)


class InPlaceVersionWriter:
    """Writes a new version into a manifest by editing the text of the file.

    Serializing a parsed document back to text loses everything the parser threw away:
    comments, blank lines, key order, and the author's choice of quoting and indentation.
    A version bump changes a handful of characters and has no business reflowing a file,
    so manifests that can be edited in place do that instead.

    Subclasses supply a parser and an editor for their format. Every edit is checked
    before it lands: an editor that cannot place the version returns ``None``, and an
    edit whose text does not parse back to the original data with only the version
    changed is discarded. Either outcome falls back to rewriting the whole document, so
    the worst case is the behavior of a format that cannot be edited in place at all.
    """

    def _parse_text(self, text: str) -> T.Any:
        """Parse a document, raising this format's parse error if it is malformed."""
        raise NotImplementedError

    def _replace_version_text(self, text: str, loc: T.Sequence[str | int], version: str) -> str | None:
        """Return ``text`` with the version at ``loc`` replaced, or None to decline."""
        raise NotImplementedError

    def _write_version_in_place(self, version: str) -> bool:
        """Rewrite just the version in the file on disk, leaving the rest of it untouched.

        Returns False when the version could not be replaced safely, so that the caller
        can fall back to rewriting the whole document.
        """
        path = self._full_path()  # type: ignore[attr-defined]
        with open(path, encoding="utf-8", newline="") as f:
            original = f.read()

        try:
            edited = self._replace_version_text(original, self.loc, version)  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 - an editor bug must never corrupt a manifest
            logger.debug(f"Failed to edit the version in {path} in place", exc_info=True)
            return False
        if edited is None or not self._edit_is_faithful(original, edited, version):
            return False

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(edited)
        return True

    def _edit_is_faithful(self, original: str, edited: str, version: str) -> bool:
        """Whether an edited document parses to the original data with only the version changed."""
        loc = self.loc  # type: ignore[attr-defined]
        try:
            edited_doc = self._parse_text(edited)
            expected_doc = self._parse_text(original)
        except Exception:  # noqa: BLE001 - any parse failure means the edit is not trustworthy
            return False
        p = expected_doc
        try:
            for k in loc[:-1]:
                p = p[k]
            p[loc[-1]] = version
        except (KeyError, IndexError, TypeError):
            return False
        return edited_doc == expected_doc

    def _write_version(self, version: str) -> None:
        """Write the version, preferring an in-place edit and warning when falling back."""
        if not self._write_version_in_place(version):
            logger.warning(
                f"Could not update the version in place in {self._full_path()}; rewriting the whole "  # type: ignore[attr-defined]
                "file. Comments and formatting in this file may not be preserved."
            )
            self._write_doc()  # type: ignore[attr-defined]
