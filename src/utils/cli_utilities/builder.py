"""CLI parser construction utilities."""

from __future__ import annotations

import argparse

from src.utils.cli_utilities.handlers import get_cli_command_handlers
from src.utils.cli_utilities.interfaces import CliCommandHandler


def build_parser(
    handlers: tuple[CliCommandHandler, ...] | None = None,
) -> argparse.ArgumentParser:
    """Build the shared CLI parser."""

    parser = argparse.ArgumentParser(description="KeepClicking CLI runner")
    for handler in handlers or get_cli_command_handlers():
        handler.register(parser)
    return parser
