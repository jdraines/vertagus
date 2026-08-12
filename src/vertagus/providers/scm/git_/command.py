"""A thin, argument-vector-only wrapper around the ``git`` executable.

Vertagus needs about a dozen git operations. Running them through
:mod:`subprocess` with an explicit argument vector -- never a shell, never a
format string -- keeps the command surface small enough to audit, and removes a
dependency whose published API forwards caller-supplied strings into git option
position.

This class does not, on its own, make a value safe: git will still read a
positional argument beginning with ``-`` as an option. Callers validate values
with :mod:`vertagus.providers.scm.git_.validation` before passing them here.
"""

import os
import subprocess
from collections.abc import Mapping, Sequence
from logging import getLogger

from vertagus.errors import VertagusError

from .validation import validate_config_key, validate_config_value

logger = getLogger(__name__)


class GitCommandError(VertagusError):
    """Raised when a git invocation exits non-zero."""

    def __init__(self, argv: Sequence[str], returncode: int, stderr: str):
        self.argv = list(argv)
        self.returncode = returncode
        self.stderr = stderr.strip()
        super().__init__(f"`{' '.join(self.argv)}` exited with status {returncode}: {self.stderr}")


class GitNotFoundError(VertagusError):
    """Raised when no ``git`` executable is available."""


class GitCommand:
    """Runs git commands against a single repository."""

    def __init__(self, root: str, config: Mapping[str, str] | None = None):
        self.root = os.path.abspath(root)
        if not os.path.isdir(self.root):
            raise VertagusError(f"No such directory: {self.root!r}")
        self._config = dict(config or {})
        for key, value in self._config.items():
            validate_config_key(key)
            validate_config_value(value, f"git config value for {key}")

    def _argv(self, args: Sequence[str], config: Mapping[str, str] | None = None) -> list[str]:
        argv = ["git", "-C", self.root]
        merged = {**self._config, **(config or {})}
        for key, value in merged.items():
            validate_config_key(key)
            validate_config_value(value, f"git config value for {key}")
            argv += ["-c", f"{key}={value}"]
        for arg in args:
            if not isinstance(arg, str):
                raise TypeError(f"git arguments must be strings, got {arg!r}")
            if "\x00" in arg:
                raise ValueError(f"git arguments may not contain NUL, got {arg!r}")
        return argv + list(args)

    def run(
        self,
        *args: str,
        config: Mapping[str, str] | None = None,
        check: bool = True,
    ) -> str:
        """Run a git command and return its stdout.

        Args:
            args: The git subcommand and its arguments, already validated.
            config: Per-invocation ``-c key=value`` settings.
            check: When true, a non-zero exit raises :class:`GitCommandError`.

        Returns:
            The command's stdout, with trailing whitespace stripped.
        """
        argv = self._argv(args, config)
        logger.debug(f"Running {argv}")
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat"}
        try:
            # argv form, shell=False; values are validated by callers before they get here.
            completed = subprocess.run(
                argv,
                cwd=self.root,
                capture_output=True,
                text=True,
                env=env,
                shell=False,
                check=False,
            )
        except FileNotFoundError as e:
            raise GitNotFoundError("The `git` executable was not found on PATH.") from e
        if check and completed.returncode != 0:
            raise GitCommandError(argv, completed.returncode, completed.stderr)
        return completed.stdout.rstrip("\n")
