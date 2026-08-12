class VertagusError(Exception):
    """Base class for errors raised by vertagus."""


class ConfigurationError(VertagusError):
    """Raised when a vertagus configuration is invalid.

    The CLI catches this and prints the message on its own, without a traceback,
    so the message should read as user-facing guidance.
    """
