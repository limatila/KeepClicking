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
    def _contains_token(cls, tokens: list[str], valid_tokens: set[str]) -> bool:
        return any(token in valid_tokens for token in tokens)

    @classmethod
    def ordered_text_matchers(cls) -> list[tuple[str, "MouseCommandAction"]]:
        return [
            ("double click", cls.DOUBLE_CLICK),
            ("right click", cls.RIGHT_CLICK),
            ("scroll", cls.SCROLL),
            ("mouse", cls.MOVE),
            ("move", cls.MOVE),
            ("stop", cls.STOP),
            ("click", cls.CLICK),
        ]

    @classmethod
    def get_choice_by_text(cls, text: str) -> "MouseCommandAction | None":
        normalized_text = text.strip().lower()
        normalized_tokens = normalized_text.split()

        if cls._contains_token(normalized_tokens, {"double", "two", "too", "to", "2"}) and cls._contains_token(
            normalized_tokens,
            {"click"},
        ):
            return cls.DOUBLE_CLICK

        if cls._contains_token(normalized_tokens, {"right"}) and cls._contains_token(
            normalized_tokens,
            {"click"},
        ):
            return cls.RIGHT_CLICK

        for action_text, action_choice in cls.ordered_text_matchers():
            action_tokens = action_text.split()
            window_size = len(action_tokens)

            for start_index in range(len(normalized_tokens) - window_size + 1):
                if normalized_tokens[start_index:start_index + window_size] == action_tokens:
                    return action_choice

            if action_text == normalized_text:
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

    @classmethod
    def get_choice_by_text(cls, text: str) -> "CommandDirection | None":
        normalized_tokens = text.strip().lower().split()

        for direction in cls:
            direction_tokens = direction.value.split()
            window_size = len(direction_tokens)

            for start_index in range(len(normalized_tokens) - window_size + 1):
                if normalized_tokens[start_index:start_index + window_size] == direction_tokens:
                    return direction

        return None
