"""CLI argument registration and dispatch helpers."""

from src.utils.cli_utilities.builder import build_parser
from src.utils.cli_utilities.handlers import get_cli_command_handlers
from src.utils.cli_utilities.resolver import resolve_cli_command
from src.utils.cli_utilities.results import CliCommandResult

__all__ = [
    "CliCommandResult",
    "build_parser",
    "get_cli_command_handlers",
    "resolve_cli_command",
]
