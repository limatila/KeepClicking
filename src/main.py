"""Main KeepClicking application entrypoint."""

from __future__ import annotations

from src.core.config import AppConfig, get_config
from src.core.logging import CORE_LOGGER, configure_logging
from src.utils.cli_utilities import resolve_cli_command


def build_application_runner(config: AppConfig):
    """Build the application runner using the current runtime config."""

    from src.command_mapper.normalizer_dispatchers import resolve_command_normalizer
    from src.command_mapper.parser import MouseCommandParser
    from src.command_mapper.validator import MouseCommandValidator
    from src.service.application_runner import MouseApplicationRunner
    from src.service.hardware_controller import PyAutoGuiMouseController
    from src.speech.offline_adapters.offline_vosk_adapter import VoskSpeechAdapter
    from src.speech.wakeword.engine import OpenWakeWordEngine

    return MouseApplicationRunner(
        adapter=VoskSpeechAdapter(
            config, OpenWakeWordEngine(config)
        ),
        normalizer=resolve_command_normalizer(config.speech_language),
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=PyAutoGuiMouseController(),
        config=config,
    )


def run_application(config: AppConfig) -> int:
    """Run the interactive voice pipeline."""

    CORE_LOGGER.info("Starting KeepClicking application runner...")
    build_application_runner(config).run()
    return 0


def main(argv: list[str] | None = None) -> int:
    config = get_config()
    configure_logging(config)

    command = resolve_cli_command(argv, config)
    if command.should_dispatch:
        return command.dispatch()

    return run_application(config)


if __name__ == "__main__":
    raise SystemExit(main())
