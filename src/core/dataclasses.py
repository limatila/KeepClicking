from dataclasses import dataclass

from src.core.choices import BaseCommandAction, CommandDirection, MouseCommandAction
from src.core.config import get_config

app_config = get_config()


@dataclass(slots=True)
class BaseCommand:
    """Structured command used across parser, validator, and executor."""

    action: BaseCommandAction
    amount: int = 1


@dataclass(slots=True)
class MouseCommand(BaseCommand):
    """Structured command used across parser, validator, and executor."""

    action: MouseCommandAction
    amount: int | None = None
    direction: CommandDirection | None = None

    def __post_init__(self) -> None:
        if self.amount is not None:
            return

        amount_per_type: dict[MouseCommandAction, int] = {
            MouseCommandAction.STOP: 0,
            MouseCommandAction.CLICK: 1,
            MouseCommandAction.DOUBLE_CLICK: 2,
            MouseCommandAction.RIGHT_CLICK: 1,
            MouseCommandAction.SCROLL: (
                app_config.mouse_scroll_units if app_config else 0
            ),
            MouseCommandAction.MOVE: (
                app_config.mouse_movement_pixels if app_config else 0
            ),
        }
        self.amount = amount_per_type.get(self.action, self.amount)
