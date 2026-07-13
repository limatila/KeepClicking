from src.command_mapper.parser import MouseCommandParser
from src.core.choices import MouseCommandAction, CommandDirection


def test_parse_click():
    parser = MouseCommandParser()

    result = parser.parse("click")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.CLICK
    assert result.error is None


def test_parse_move_right():
    parser = MouseCommandParser()

    result = parser.parse("move right")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.MOVE
    assert result.command.direction == CommandDirection.RIGHT


def test_parse_mouse_up_as_move_up():
    parser = MouseCommandParser()

    result = parser.parse("mouse up")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.MOVE
    assert result.command.direction == CommandDirection.UP
    assert result.error is None


def test_parse_noisy_mouse_up_as_move_up():
    parser = MouseCommandParser()

    result = parser.parse("a mouse up")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.MOVE
    assert result.command.direction == CommandDirection.UP
    assert result.error is None


def test_parse_double_click_without_matching_click_first():
    parser = MouseCommandParser()

    result = parser.parse("double click")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.DOUBLE_CLICK
    assert result.error is None


def test_parse_noisy_double_click():
    parser = MouseCommandParser()

    result = parser.parse("please double click now")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.DOUBLE_CLICK
    assert result.error is None


def test_parse_two_click_as_double_click():
    parser = MouseCommandParser()

    result = parser.parse("two click")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.DOUBLE_CLICK
    assert result.error is None


def test_parse_right_click():
    parser = MouseCommandParser()

    result = parser.parse("right click")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.RIGHT_CLICK
    assert result.error is None


def test_parse_scroll_down():
    parser = MouseCommandParser()

    result = parser.parse("please scroll down now")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.SCROLL
    assert result.command.direction == CommandDirection.DOWN
    assert result.error is None


def test_parse_scroll_up():
    parser = MouseCommandParser()

    result = parser.parse("scroll up")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.SCROLL
    assert result.command.direction == CommandDirection.UP
    assert result.error is None


def test_parse_scroll_without_direction():
    parser = MouseCommandParser()

    result = parser.parse("scroll")

    assert result.command is None
    assert result.error is not None
    assert result.error.reason == "missing_command_direction"


def test_parse_unknown():
    parser = MouseCommandParser()

    result = parser.parse("nonsense")

    assert result.command is None
    assert result.error is not None


def test_parser_removes_direction_for_non_move_commands():
    parser = MouseCommandParser()

    result = parser.parse("click up")

    assert result.command is not None
    assert result.command.action == MouseCommandAction.CLICK
    assert result.command.direction is None


def test_parser_resets_state_between_calls():
    parser = MouseCommandParser()

    first = parser.parse("nonsense")
    second = parser.parse("click")

    assert first.command is None
    assert first.error is not None
    assert second.command is not None
    assert second.command.action == MouseCommandAction.CLICK
    assert second.error is None
