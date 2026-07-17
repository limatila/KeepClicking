"""Command validator interfaces and implementations."""

from __future__ import annotations

from src.core.choices import MouseCommandAction, CommandShape
from src.core.errors import ValidationError
from src.core.logging import VALIDATOR_LOGGER

from src.command_mapper.command_shapes import get_command_shape
from src.command_mapper.dataclasses import ValidationResult
from src.command_mapper.interfaces import CommandValidator


class MouseCommandValidator(CommandValidator):
    """Deterministic validator for MVP command objects."""

    @property
    def validations_listing(self):
        return [
            self.rule_valid_action,
            self.rule_positive_amount,
            self.rule_direction_matches_action_shape,
        ]

    def rule_valid_action(self) -> ValidationResult:
        if not isinstance(self.command.action, MouseCommandAction):
            # VALIDATOR_LOGGER.debug("validation_failed: invalid_action at command")
            raise ValidationError(reason="invalid_action", field="action")
    
    def rule_positive_amount(self) -> ValidationResult:
        if self.command.amount < 0:
            VALIDATOR_LOGGER.debug("validation_failed: non_positive_amount")
            raise ValidationError(reason="non_positive_amount", field="amount")
    
    def rule_direction_matches_action_shape(self) -> ValidationResult:
        command_shape: "CommandShape" = get_command_shape(self.command.action)
        validation_reason = command_shape.validate_direction(self.command.direction)
        
        if validation_reason is None:
            return None

        VALIDATOR_LOGGER.debug("validation_failed: %s", validation_reason)
        raise ValidationError(reason=validation_reason, field="direction")
