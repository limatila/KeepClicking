"""Command parser interfaces and implementations."""

from __future__ import annotations

import logging

from src.core.dataclasses import MouseCommand
from src.core.choices import MouseCommandAction, CommandDirection

from src.commands.dataclasses import ParseError, ParseResult
from src.commands.interfaces import CommandParser

LOGGER = logging.getLogger("baseLogger.parser")


class MouseCommandParser(CommandParser):
	"""Deterministic parser for MVP command phrases."""

	def __init__(self):
		self.parsed_mouse_command_choice = None
		self.parsed_mouse_command = None
		self.error = None

	def parse(self, text: str) -> ParseResult:	
		text = text.lower().strip()

		#* Parse action type
		for action_choice_value in MouseCommandAction.list_choices_values():
			if action_choice_value in text:
				parsed_mouse_command_value = action_choice_value

				self.parsed_mouse_command_choice = MouseCommandAction.get_choice_by_value(parsed_mouse_command_value)
				self.parsed_mouse_command = MouseCommand(action=self.parsed_mouse_command_choice)
				
				break
		else:
			self.error = ParseError(reason="unrecognized_command", raw_text=text)
			return ParseResult(None, self.error)

		#* Parse action direction (if applicable)
		if self.parsed_mouse_command_choice in [MouseCommandAction.MOVE]:
			for direction_choice_value in CommandDirection.list_choices_values():
				if direction_choice_value in text:
					parsed_direction_value = direction_choice_value
					
					parsed_direction_choice = CommandDirection.get_choice_by_value(parsed_direction_value)
					self.parsed_mouse_command.direction = parsed_direction_choice
					
					break
			else:
				self.error = ParseError(reason="missing_command_direction", raw_text=text)
				return ParseResult(None, self.error)
		
		return ParseResult(self.parsed_mouse_command, self.error)
