from dataclasses import dataclass

from src.core.dataclasses import MouseCommand
from src.core.errors import ValidationError


@dataclass(slots=True)
class ParseError:
	"""Describes a parsing failure for a command string."""

	reason: str
	raw_text: str


@dataclass(slots=True)
class ParseResult:
	"""Represents the outcome of a parse attempt."""

	command: MouseCommand | None
	error: ParseError | None


@dataclass(slots=True)
class ValidationResult:
	"""Represents the outcome of a validation attempt."""

	command: MouseCommand
	error: ValidationError | None