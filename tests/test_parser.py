from src.commands.parser import MouseCommandParser
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