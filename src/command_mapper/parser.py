"""Command parser interfaces and implementations."""

from __future__ import annotations

from src.core.choices import CommandShape, MouseCommandAction
from src.core.dataclasses import MouseCommand
from src.core.logging import PARSER_LOGGER

from src.command_mapper.command_shapes import get_command_shape
from src.command_mapper.dataclasses import ParseError, ParseResult
from src.command_mapper.interfaces import CommandParser


class MouseCommandParser(CommandParser):
    """Deterministic parser for canonical command phrases."""

    def __init__(self):
        self.parsed_mouse_command_choice = None
        self.parsed_mouse_command = None
        self.error = None

    def parse(self, text: str) -> ParseResult:
        self.parsed_mouse_command_choice = None
        self.parsed_mouse_command = None
        self.error = None

        text = text.lower().strip()

        #* Parse action type
        self.parsed_mouse_command_choice = MouseCommandAction.resolve_choice_by_full_text(text)
        
        if self.parsed_mouse_command_choice is None:
            self.error = ParseError(reason="unrecognized_command", raw_text=text)
            return ParseResult(None, self.error)

        self.parsed_mouse_command = MouseCommand(action=self.parsed_mouse_command_choice)

        #* Parse action direction (if applicable)
        command_shape: "CommandShape" = get_command_shape(self.parsed_mouse_command_choice)
        if command_shape.requires_direction:
            parsed_direction_choice = command_shape.resolve_direction_by_text(text)
            
            if parsed_direction_choice is None:
                self.error = ParseError(reason="missing_command_direction", raw_text=text)
                return ParseResult(None, self.error)
            
            self.parsed_mouse_command.direction = parsed_direction_choice

        return ParseResult(self.parsed_mouse_command, self.error)
