from dataclasses import dataclass


@dataclass(slots=True)
class MouseExecutionResult:
	"""Represents the outcome of a mouse command execution."""

	stopped: bool
	error: str | None