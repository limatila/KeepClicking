from src.commands.validator import MouseCommandValidator
from src.core.dataclasses import MouseCommand
from src.core.choices import MouseCommandAction, CommandDirection


def test_validator_accepts_move():
    validator = MouseCommandValidator()
    command = MouseCommand(action=MouseCommandAction.MOVE, direction=CommandDirection.UP, amount=5)
    
    result = validator.validate(command)
    
    assert result.command is not None
    assert result.error is None


def test_validator_rejects_direction_for_click():
    validator = MouseCommandValidator()
    command = MouseCommand(action=MouseCommandAction.CLICK, direction=CommandDirection.UP)
    
    result = validator.validate(command)
    
    assert result.error is not None #! todo verify if parser cleans direction before validation
    assert result.error.field == "direction"


def test_validator_rejects_non_positive_amount():
    validator = MouseCommandValidator()
    command = MouseCommand(action=MouseCommandAction.MOVE, direction=CommandDirection.UP, amount=0)
    
    result = validator.validate(command)
    
    assert result.error is not None
    assert result.error.field == "amount"
