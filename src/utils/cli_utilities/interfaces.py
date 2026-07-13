"""Interfaces for CLI command handlers."""

from __future__ import annotations

import argparse
from typing import Protocol

from src.core.config import AppConfig


class CliCommandHandler(Protocol):
    """Encapsulates a CLI command registration and execution flow."""

    name: str

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Register parser arguments owned by this command."""

    def is_selected(self, args: argparse.Namespace) -> bool:
        """Return whether this command should handle parsed arguments."""

    def handle(self, args: argparse.Namespace, config: AppConfig) -> int:
        """Execute the command and return the process exit code."""
