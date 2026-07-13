import pytest

import src.utils.cli_utilities as cli_utilities
from src.core.config import get_config


def test_resolve_cli_command_matches_list_audio_devices():
    command = cli_utilities.resolve_cli_command(
        ["--list-audio-devices"],
        get_config(),
    )

    assert command.should_dispatch is True
    assert command.handler is not None
    assert command.handler.name == "list_audio_devices"


def test_resolve_cli_command_without_flags_returns_no_dispatch():
    command = cli_utilities.resolve_cli_command([], get_config())

    assert command.should_dispatch is False


def test_resolve_cli_command_unknown_arg_raises_parser_error():
    with pytest.raises(SystemExit):
        cli_utilities.resolve_cli_command(["--unknown-flag"], get_config())


def test_list_audio_devices_dispatch_uses_resolver(monkeypatch):
    called = {"count": 0}

    def fake_list_cli_input_devices(self):
        called["count"] += 1

    monkeypatch.setattr(
        "src.speech.audio_device_resolver.AudioDeviceResolver.list_cli_input_devices",
        fake_list_cli_input_devices,
    )

    command = cli_utilities.resolve_cli_command(
        ["--list-audio-devices"],
        get_config(),
    )

    assert command.dispatch() == 0
    assert called["count"] == 1
