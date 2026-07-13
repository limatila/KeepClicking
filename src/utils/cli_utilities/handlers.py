"""Registered CLI command handlers."""

from __future__ import annotations

from src.utils.cli_utilities.interfaces import CliCommandHandler
from src.utils.cli_utilities.list_audio_devices import ListAudioDevicesCommand


def get_cli_command_handlers() -> tuple[CliCommandHandler, ...]:
    """Return the registered CLI handlers."""

    return (ListAudioDevicesCommand(),)
