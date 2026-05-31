"""Command parser interfaces and implementations."""

from __future__ import annotations

import logging

from src.core.dataclasses import MouseCommand
from src.core.config import AppConfig
from src.core.choices import MouseCommandAction, CommandDirection

from src.commands.dataclasses import ParseError, ParseResult
from src.commands.interfaces import CommandParser

LOGGER = logging.getLogger("baseLogger.parser")


class MouseCommandParser(CommandParser):
	"""Deterministic parser for MVP command phrases."""

	def parse(self, text: str, config: AppConfig) -> ParseResult:
		def _success(command: MouseCommand) -> ParseResult:
			# LOGGER.debug("parsed_command: %s", command.action)
			return ParseResult(command, None)

		if text == "click":
			return _success(MouseCommand(action=MouseCommandAction.CLICK))
		
		if text == "double click":
			return _success(MouseCommand(action=MouseCommandAction.DOUBLE_CLICK, amount=2))
		
		if text == "right click":
			return _success(MouseCommand(action=MouseCommandAction.RIGHT_CLICK))
		
		if text == "scroll up":
			return _success(
				MouseCommand(
					action=MouseCommandAction.SCROLL,
					direction=CommandDirection.UP,
					amount=config.scroll_units,
				)
			)
		
		if text == "scroll down":
			return _success(
				MouseCommand(
					action=MouseCommandAction.SCROLL,
					direction=CommandDirection.DOWN,
					amount=config.scroll_units,
				)
			)
		
		if text == "move up":
			return _success(
				MouseCommand(
					action=MouseCommandAction.MOVE,
					direction=CommandDirection.UP,
					amount=config.move_pixels,
				)
			)
		
		if text == "move down":
			return _success(
				MouseCommand(
					action=MouseCommandAction.MOVE,
					direction=CommandDirection.DOWN,
					amount=config.move_pixels,
				)
			)
		
		if text == "move left":
			return _success(
				MouseCommand(
					action=MouseCommandAction.MOVE,
					direction=CommandDirection.LEFT,
					amount=config.move_pixels,
				)
			)
		
		if text == "move right":
			return _success(
				MouseCommand(
					action=MouseCommandAction.MOVE,
					direction=CommandDirection.RIGHT,
					amount=config.move_pixels,
				)
			)
		
		if text == "stop":
			return _success(MouseCommand(action=MouseCommandAction.STOP))
		
		LOGGER.debug("parse_failed: %s", text)
		return ParseResult(None, ParseError(reason="unrecognized_command", raw_text=text))
