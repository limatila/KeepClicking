from src.commands.validator import RuleBasedCommandValidator
from src.core.models import Command, CommandAction, CommandDirection


def test_validator_accepts_move():
    validator = RuleBasedCommandValidator()
    command = Command(action=CommandAction.MOVE, direction=CommandDirection.UP, amount=5)
    result = validator.validate(command)
    assert result.command is not None
    assert result.error is None


def test_validator_rejects_direction_for_click():
    validator = RuleBasedCommandValidator()
    command = Command(action=CommandAction.CLICK, direction=CommandDirection.UP)
    result = validator.validate(command)
    assert result.command is None
    assert result.error is not None
    assert result.error.field == "direction"


def test_validator_rejects_non_positive_amount():
    validator = RuleBasedCommandValidator()
    command = Command(action=CommandAction.MOVE, direction=CommandDirection.UP, amount=0)
    result = validator.validate(command)
    assert result.command is None
    assert result.error is not None
    assert result.error.field == "amount"
