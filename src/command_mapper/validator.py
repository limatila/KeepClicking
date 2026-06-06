"""Command validator interfaces and implementations."""

from __future__ import annotations

from src.core.choices import MouseCommandAction, CommandDirection
from src.core.errors import ValidationError
from src.core.logging import VALIDATOR_LOGGER

from src.command_mapper.dataclasses import ValidationResult
from src.command_mapper.interfaces import CommandValidator


class MouseCommandValidator(CommandValidator):
	"""Deterministic validator for MVP command objects."""

	@property
	def validations_listing(self):
		return [
			self.rule_valid_action,
			self.rule_positive_amount,
			self.rule_direction_to_move_screen,
			self.rule_direction_in_moving_action
		]

	def rule_valid_action(self) -> ValidationResult:
		if not isinstance(self.command.action, MouseCommandAction):
			# VALIDATOR_LOGGER.debug("validation_failed: invalid_action at command")
			raise ValidationError(reason="invalid_action", field="action")
	
	def rule_positive_amount(self) -> ValidationResult:
		if self.command.amount < 0:
			VALIDATOR_LOGGER.debug("validation_failed: non_positive_amount")
			raise ValidationError(reason="non_positive_amount", field="amount")
	
	def rule_direction_to_move_screen(self) -> ValidationResult:
		if self.command.action in (MouseCommandAction.MOVE):
			if self.command.direction is None:
				VALIDATOR_LOGGER.debug("validation_failed: missing_direction")
				raise ValidationError(reason="missing_direction", field="direction")
			
			if not isinstance(self.command.direction, CommandDirection):
				VALIDATOR_LOGGER.debug("validation_failed: invalid_direction")
				raise ValidationError(reason="invalid_direction", field="direction")
	
	def rule_direction_in_moving_action(self) -> ValidationResult:
		if self.command.action not in (MouseCommandAction.MOVE):
			if self.command.direction is not None:
				VALIDATOR_LOGGER.debug("validation_failed: direction_not_applicable")
				raise ValidationError(reason="direction_not_applicable", field="direction")
