"""Dev CLI runner for the KeepClicking voice pipeline."""

from __future__ import annotations

from src.core.config import get_config
from src.core.logging import CORE_LOGGER, configure_logging
from src.main import run_application
from src.utils.cli_utilities import resolve_cli_command


def main(argv: list[str] | None = None) -> int:
    config = get_config(debug_mode=True)
    configure_logging(config)

    command = resolve_cli_command(argv, config)
    if command.should_dispatch:
        return command.dispatch()

    CORE_LOGGER.info("![DEV] Starting KeepClicking CLI runner...\n")
    return run_application(config)


if __name__ == "__main__":
    raise SystemExit(main())
