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


def test_validator_rejects_negative_amount():
    validator = MouseCommandValidator()
    command = MouseCommand(action=MouseCommandAction.MOVE, direction=CommandDirection.UP, amount=-1)
    command_2 = MouseCommand(action=MouseCommandAction.MOVE, direction=CommandDirection.UP, amount=-5)
    
    result = validator.validate(command)
    result_2 = validator.validate(command_2)
    
    assert result.error is not None
    assert result.error.field == "amount"
    assert result_2.error is not None
    assert result_2.error.field == "amount"
