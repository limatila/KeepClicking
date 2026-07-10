from src.command_mapper.validator import MouseCommandValidator
from src.core.dataclasses import MouseCommand
from src.core.choices import MouseCommandAction, CommandDirection


def test_validator_accepts_move():
    validator = MouseCommandValidator()
    command = MouseCommand(
        action=MouseCommandAction.MOVE,
        direction=CommandDirection.UP,
        amount=5,
    )

    result = validator.validate(command)

    assert result.command is not None
    assert result.error is None


def test_validator_accepts_scroll_up():
    validator = MouseCommandValidator()
    command = MouseCommand(
        action=MouseCommandAction.SCROLL,
        direction=CommandDirection.UP,
        amount=5,
    )

    result = validator.validate(command)

    assert result.command is not None
    assert result.error is None


def test_validator_rejects_direction_for_click():
    validator = MouseCommandValidator()
    command = MouseCommand(action=MouseCommandAction.CLICK, direction=CommandDirection.UP)

    result = validator.validate(command)

    assert result.error is not None
    assert result.error.field == "direction"


def test_validator_rejects_negative_amount():
    validator = MouseCommandValidator()
    command = MouseCommand(
        action=MouseCommandAction.MOVE,
        direction=CommandDirection.UP,
        amount=-1,
    )
    command_2 = MouseCommand(
        action=MouseCommandAction.MOVE,
        direction=CommandDirection.UP,
        amount=-5,
    )

    result = validator.validate(command)
    result_2 = validator.validate(command_2)

    assert result.error is not None
    assert result.error.field == "amount"
    assert result_2.error is not None
    assert result_2.error.field == "amount"


def test_validator_rejects_horizontal_scroll():
    validator = MouseCommandValidator()
    command = MouseCommand(
        action=MouseCommandAction.SCROLL,
        direction=CommandDirection.LEFT,
        amount=5,
    )

    result = validator.validate(command)

    assert result.error is not None
    assert result.error.reason == "invalid_scroll_direction"


def test_validator_resets_state_between_calls():
    validator = MouseCommandValidator()
    invalid = MouseCommand(action=MouseCommandAction.CLICK, direction=CommandDirection.UP)
    valid = MouseCommand(
        action=MouseCommandAction.MOVE,
        direction=CommandDirection.UP,
        amount=5,
    )

    first = validator.validate(invalid)
    second = validator.validate(valid)

    assert first.error is not None
    assert second.error is None
