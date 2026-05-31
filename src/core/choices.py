"""Domain command models."""

from __future__ import annotations


from src.core.interfaces.choices import BaseChoice


class BaseCommandAction(BaseChoice):
	"""Supported command actions listing, choices per device type."""
	pass


class MouseCommandAction(BaseCommandAction):
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
