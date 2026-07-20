"""Registered CLI command handlers."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from src.core.config import AppConfig
from src.utils.cli_utilities.interfaces import CliCommandHandler


@dataclass(frozen=True, slots=True)
class ListAudioDevicesCommand:
    """List available audio input devices and exit."""

    name: str = "list_audio_devices"

    def register(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--list-audio-devices",
            action="store_true",
            help="Display all input-capable devices currently available for .env selection",
        )

    def is_selected(self, args: argparse.Namespace) -> bool:
        return bool(getattr(args, "list_audio_devices", False))

    def handle(self, args: argparse.Namespace, config: AppConfig) -> int:
        del args
        del config

        from src.speech.audio_device_resolver import AudioDeviceResolver

        AudioDeviceResolver().list_cli_input_devices()
        return 0


def get_cli_command_handlers() -> tuple[CliCommandHandler, ...]:
    """Return the registered CLI handlers."""

    return (ListAudioDevicesCommand(),)
