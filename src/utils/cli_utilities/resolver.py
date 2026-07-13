"""CLI command resolution utilities."""

from __future__ import annotations

from src.core.config import AppConfig
from src.utils.cli_utilities.builder import build_parser
from src.utils.cli_utilities.handlers import get_cli_command_handlers
from src.utils.cli_utilities.interfaces import CliCommandHandler
from src.utils.cli_utilities.results import CliCommandResult


def resolve_cli_command(
    argv: list[str] | None,
    config: AppConfig,
    handlers: tuple[CliCommandHandler, ...] | None = None,
) -> CliCommandResult:
    """Resolve a CLI command from parsed arguments."""

    available_handlers = handlers or get_cli_command_handlers()
    args = build_parser(available_handlers).parse_args(argv)

    for handler in available_handlers:
        if handler.is_selected(args):
            return CliCommandResult(handler=handler, args=args, config=config)

    return CliCommandResult(args=args, config=config)
