from src.commands.parser import RuleBasedCommandParser
from src.core.config import get_config
from src.core.models import CommandAction, CommandDirection


def test_parse_click():
    parser = RuleBasedCommandParser()
    result = parser.parse("click", get_config())
    assert result.command is not None
    assert result.command.action == CommandAction.CLICK
    assert result.error is None


def test_parse_move_right():
    parser = RuleBasedCommandParser()
    result = parser.parse("move right", get_config())
    assert result.command is not None
    assert result.command.action == CommandAction.MOVE
    assert result.command.direction == CommandDirection.RIGHT


def test_parse_unknown():
    parser = RuleBasedCommandParser()
    result = parser.parse("nonsense", get_config())
    assert result.command is None
    assert result.error is not None
