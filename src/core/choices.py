"""Domain command models."""

from __future__ import annotations
from dataclasses import dataclass

from src.core.interfaces.choices import BaseChoice


class SpeechLanguage(BaseChoice):
    """Supported speech normalization locales."""

    EN_US = "en_us"
    PT_BR = "pt_br"


class BaseCommandAction(BaseChoice):
    """Supported command actions listing, choices per device type."""


class KeyboardCommandAction(BaseCommandAction):
    """ TODO/FUTURE: Supported command actions for keyboard commands."""


class MouseCommandAction(BaseCommandAction):
    """Supported command actions for the MVP pipeline."""

    STOP = "stop"  # user cancel word
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    MOVE = "move"
    # DRAG = "drag" # TODO: drag to directions
    
    def requires_direction(self) -> bool:
        return self.value in (
            MouseCommandAction.SCROLL,
            MouseCommandAction.MOVE
        )


class CommandDirection(BaseChoice):
    """Supported directions for scroll and move commands."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True, slots=True)
class CommandShape:
    """Describe how a command action can combine with command directions, in valid shapes."""

    action: MouseCommandAction
    allowed_directions: tuple[CommandDirection, ...] = ()
    invalid_direction_reason: str = "invalid_direction"

    @property
    def normalized_value(self) -> str:
        return self.action.value.replace("_", " ")

    @property
    def requires_direction(self) -> bool:
        return len(self.allowed_directions) > 0

    def canonical_phrases(self) -> tuple[str, ...]:
        if not self.requires_direction:
            return (self.normalized_value,)

        return tuple(
            f"{self.normalized_value} {direction.value}"
            for direction in self.allowed_directions
        )

    def resolve_direction_by_text(self, text: str) -> CommandDirection | None:
        if not self.requires_direction:
            return None
        return CommandDirection.resolve_choice_by_full_text(text)

    def validate_direction(self, direction: object) -> str | None:
        if self.requires_direction:
            if direction is None:
                return "missing_direction"

            if not isinstance(direction, CommandDirection):
                return "invalid_direction"

            if direction not in self.allowed_directions:
                return self.invalid_direction_reason

            return None

        if direction is not None:
            return "direction_not_applicable"

        return None
