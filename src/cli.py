"""Dev-ambient CLI runner for testing and development."""

from __future__ import annotations

import argparse

from src.core.logging import CORE_LOGGER
from src.core.config import get_config

APP_CONFIG = get_config(debug_mode=True)


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KeepClicking development runner")
    
    parser.add_argument(
        "--list-audio-devices",
        action="store_true",
        help="Print input-capable devices resolved by sounddevice and exit",
    )

    return parser


def list_audio_devices() -> int:
    from src.speech.audio_device_resolver import AudioDeviceResolver
    
    devices_resolver = AudioDeviceResolver()
    devices_resolver.list_cli_input_devices()

    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    
    if args.list_audio_devices:
        return list_audio_devices()

    from src.service.application_runner import MouseApplicationRunner
    from src.speech.wakeword.engine import OpenWakeWordEngine
    from src.speech.offline_adapters.offline_vosk_adapter import VoskSpeechAdapter
    from src.command_mapper.normalizer import normalize_text
    from src.command_mapper.parser import MouseCommandParser
    from src.command_mapper.validator import MouseCommandValidator
    from src.service.hardware_controller import PyAutoGuiMouseController

    CORE_LOGGER.info("![DEV] Starting KeepClicking CLI runner...\n")
    
    runner = MouseApplicationRunner(
        adapter=VoskSpeechAdapter(
            APP_CONFIG, OpenWakeWordEngine(APP_CONFIG)
        ),
        normalizer=normalize_text,
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=PyAutoGuiMouseController(),
        config=APP_CONFIG,
    )

    runner.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
