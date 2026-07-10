"""Domain command models."""

from __future__ import annotations

from src.core.interfaces.choices import BaseChoice


class BaseCommandAction(BaseChoice):
    """Supported command actions listing, choices per device type."""
    pass

class KeyboardCommandAction(BaseCommandAction):
    """ TODO/FUTURE: Supported command actions for keyboard commands."""
    pass


class MouseCommandAction(BaseCommandAction):
    """Supported command actions for the MVP pipeline."""

    STOP = "stop" #user cancel word
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    MOVE = "move"


class CommandDirection(BaseChoice):
    """Supported directions for scroll and move commands."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
