"""Command parser interfaces and implementations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from src.core.config import AppConfig
from src.core.models import Command, CommandAction, CommandDirection

LOGGER = logging.getLogger("baseLogger.parser")


@dataclass(frozen=True)
class ParseError:
	"""Describes a parsing failure for a command string."""

	reason: str
	raw_text: str


@dataclass(frozen=True)
class ParseResult:
	"""Represents the outcome of a parse attempt."""

	command: Command | None
	error: ParseError | None


class CommandParser(Protocol):
	"""Base interface for command parsers."""

	def parse(self, text: str, config: AppConfig) -> ParseResult:
		"""Parse normalized text into a command or an error."""


class RuleBasedCommandParser:
	"""Deterministic parser for MVP command phrases."""

	def parse(self, text: str, config: AppConfig) -> ParseResult:
		def _success(command: Command) -> ParseResult:
			LOGGER.debug("parsed_command: %s", command.action)
			return ParseResult(command, None)

		if text == "click":
			return _success(Command(action=CommandAction.CLICK))
		if text == "double click":
			return _success(Command(action=CommandAction.DOUBLE_CLICK, amount=2))
		if text == "right click":
			return _success(Command(action=CommandAction.RIGHT_CLICK))
		if text == "scroll up":
			return _success(
				Command(
					action=CommandAction.SCROLL,
					direction=CommandDirection.UP,
					amount=config.scroll_units,
				)
			)
		if text == "scroll down":
			return _success(
				Command(
					action=CommandAction.SCROLL,
					direction=CommandDirection.DOWN,
					amount=config.scroll_units,
				)
			)
		if text == "move up":
			return _success(
				Command(
					action=CommandAction.MOVE,
					direction=CommandDirection.UP,
					amount=config.move_pixels,
				)
			)
		if text == "move down":
			return _success(
				Command(
					action=CommandAction.MOVE,
					direction=CommandDirection.DOWN,
					amount=config.move_pixels,
				)
			)
		if text == "move left":
			return _success(
				Command(
					action=CommandAction.MOVE,
					direction=CommandDirection.LEFT,
					amount=config.move_pixels,
				)
			)
		if text == "move right":
			return _success(
				Command(
					action=CommandAction.MOVE,
					direction=CommandDirection.RIGHT,
					amount=config.move_pixels,
				)
			)
		if text == "stop":
			return _success(Command(action=CommandAction.STOP))
		LOGGER.debug("parse_failed: %s", text)
		return ParseResult(None, ParseError(reason="unrecognized_command", raw_text=text))
