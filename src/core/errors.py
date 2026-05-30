"""Application error types."""

from __future__ import annotations


class KeepClickingError(Exception):
	"""Base class for application-level errors."""


class OptionalDependencyError(KeepClickingError):
	"""Raised when an optional dependency is missing."""


class MouseExecutionError(KeepClickingError):
	"""Raised when the mouse controller fails to execute a command."""


class AdapterError(KeepClickingError):
	"""Raised when an input adapter fails unexpectedly."""
