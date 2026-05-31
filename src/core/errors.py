"""Application error types."""


class ApplicationError(Exception):
	"""Base class for application-level errors."""


class MouseExecutionError(ApplicationError):
	"""Raised when the mouse controller fails to execute a command."""


class AdapterError(ApplicationError):
	"""Raised when an input adapter fails unexpectedly."""


class ValidationError(Exception):
	"""Describes a validation failure for a command, informing errors per field of the command."""

	def __init__(self, reason: str, field: str):
		self.reason = reason
		self.field = field
