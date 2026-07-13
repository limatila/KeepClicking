"""Result objects for resolved CLI commands."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from src.core.config import AppConfig
from src.utils.cli_utilities.interfaces import CliCommandHandler


@dataclass(frozen=True, slots=True)
class CliCommandResult:
    """Represents a matched CLI command or the absence of one."""

    handler: CliCommandHandler | None = None
    args: argparse.Namespace | None = None
    config: AppConfig | None = None

    @property
    def should_dispatch(self) -> bool:
        return self.handler is not None

    def dispatch(self) -> int:
        if self.handler is None or self.args is None or self.config is None:
            raise RuntimeError("No CLI command was resolved for the inserted args.")
        
        return self.handler.handle(self.args, self.config)
