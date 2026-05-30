"""Domain command models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BaseChoice(str, Enum):
	"""Base class for string enums used across the domain models."""


class CommandAction(BaseChoice):
	"""Supported command actions for the MVP pipeline."""

	CLICK = "click"
	DOUBLE_CLICK = "double_click"
	RIGHT_CLICK = "right_click"
	SCROLL = "scroll"
	MOVE = "move"
	STOP = "stop"


class CommandDirection(BaseChoice):
	"""Supported directions for scroll and move commands."""

	UP = "up"
	DOWN = "down"
	LEFT = "left"
	RIGHT = "right"


@dataclass(frozen=True)
class Command:
	"""Structured command used across parser, validator, and executor."""

	action: CommandAction
	amount: int = 1
	direction: CommandDirection | None = None
