from dataclasses import dataclass

from src.core.choices import (
	BaseCommandAction, MouseCommandAction,
	CommandDirection
)


@dataclass(slots=True)
class BaseCommand:
	"""Structured command used across parser, validator, and executor."""

	action: BaseCommandAction
	amount: int = 1


@dataclass(slots=True)
class MouseCommand(BaseCommand):
	"""Structured command used across parser, validator, and executor."""

	action: MouseCommandAction
	amount: int = 1
	direction: CommandDirection | None = None
