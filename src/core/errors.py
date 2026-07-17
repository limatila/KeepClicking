"""Application error types."""


class ApplicationError(Exception):
    """Base class for application-level errors."""


class MouseExecutionError(ApplicationError):
    """Raised when the mouse controller fails to execute a command."""


class AdapterError(ApplicationError):
    """Raised when an input adapter fails unexpectedly."""


class NormalizationError(ApplicationError):
    """Raised when command normalization fails structurally."""


class ValidationError(Exception):
    """Describe a validation failure for a command field."""

    def __init__(self, reason: str, field: str) -> None:
        self.reason = reason
        self.field = field
