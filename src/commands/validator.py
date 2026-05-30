"""Command validator interfaces and implementations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from src.core.models import Command, CommandAction, CommandDirection

LOGGER = logging.getLogger("baseLogger.validator")


@dataclass(frozen=True)
class ValidationError:
	"""Describes a validation failure for a command."""

	reason: str
	field: str | None


@dataclass(frozen=True)
class ValidationResult:
	"""Represents the outcome of a validation attempt."""

	command: Command | None
	error: ValidationError | None


class CommandValidator(Protocol):
	"""Base interface for command validators."""

	def validate(self, command: Command) -> ValidationResult:
		"""Validate a command and return a result object."""


class RuleBasedCommandValidator:
	"""Deterministic validator for MVP command objects."""

	def validate(self, command: Command) -> ValidationResult:
		if not isinstance(command.action, CommandAction):
			LOGGER.debug("validation_failed: invalid_action")
			return ValidationResult(
				None,
				ValidationError(reason="invalid_action", field="action"),
			)

		if command.amount <= 0:
			LOGGER.debug("validation_failed: non_positive_amount")
			return ValidationResult(
				None,
				ValidationError(reason="non_positive_amount", field="amount"),
			)

		if command.action in (CommandAction.MOVE, CommandAction.SCROLL):
			if command.direction is None:
				LOGGER.debug("validation_failed: missing_direction")
				return ValidationResult(
					None,
					ValidationError(reason="missing_direction", field="direction"),
				)
			if not isinstance(command.direction, CommandDirection):
				LOGGER.debug("validation_failed: invalid_direction")
				return ValidationResult(
					None,
					ValidationError(reason="invalid_direction", field="direction"),
				)
		else:
			if command.direction is not None:
				LOGGER.debug("validation_failed: unexpected_direction")
				return ValidationResult(
					None,
					ValidationError(reason="unexpected_direction", field="direction"),
				)

		LOGGER.debug("validation_ok: %s", command.action)
		return ValidationResult(command=command, error=None)
