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

    @classmethod
    def ordered_text_matchers(cls) -> list[tuple[str, "MouseCommandAction"]]:
        return [
            ("double click", cls.DOUBLE_CLICK),
            ("right click", cls.RIGHT_CLICK),
            ("scroll", cls.SCROLL),
            ("move", cls.MOVE),
            ("stop", cls.STOP),
            ("click", cls.CLICK),
        ]

    @classmethod
    def get_choice_by_text(cls, text: str) -> "MouseCommandAction | None":
        normalized_text = text.strip().lower()

        for action_text, action_choice in cls.ordered_text_matchers():
            if action_text in normalized_text:
                return action_choice

        return None

    def requires_direction(self) -> bool:
        return self in (self.MOVE, self.SCROLL)


class CommandDirection(BaseChoice):
    """Supported directions for scroll and move commands."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
