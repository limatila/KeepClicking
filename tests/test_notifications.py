from __future__ import annotations

from types import SimpleNamespace

import src.speech.notifications as notifications
from src.speech.notifications import (
    NoOpNotificationSoundPlayer,
    WindowsNotificationSoundPlayer,
    build_notification_sound_player,
)


def test_build_notification_sound_player_uses_windows_player(monkeypatch):
    monkeypatch.setattr(notifications.sys, "platform", "win32")

    player = build_notification_sound_player()

    assert isinstance(player, WindowsNotificationSoundPlayer)


def test_build_notification_sound_player_uses_noop_player_off_windows(monkeypatch):
    monkeypatch.setattr(notifications.sys, "platform", "linux")

    player = build_notification_sound_player()

    assert isinstance(player, NoOpNotificationSoundPlayer)


def test_windows_notification_sound_player_plays_bundled_mp3_with_mci(
    monkeypatch,
    tmp_path,
):
    sound_path = tmp_path / "notify.mp3"
    sound_path.write_bytes(b"mp3")
    commands: list[str] = []

    class FakeWinMM:
        def mciSendStringW(self, command, buffer, buffer_size, callback):
            commands.append(command)
            return 0

    fake_winmm = FakeWinMM()
    fake_ctypes = SimpleNamespace(
        WinDLL=lambda dll_name: fake_winmm,
        create_unicode_buffer=lambda size: SimpleNamespace(value=""),
    )
    monkeypatch.setitem(notifications.sys.modules, "ctypes", fake_ctypes)

    WindowsNotificationSoundPlayer(sound_path).play_wake_word_detected()

    assert commands == [
        "close keepclicking_notify",
        f'open "{sound_path}" type mpegvideo alias keepclicking_notify',
        "play keepclicking_notify from 0",
    ]
