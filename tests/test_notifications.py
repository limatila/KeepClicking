from __future__ import annotations

from types import SimpleNamespace

import src.utils.notifications as notifications
from src.utils.notifications import (
    NoNotificationSoundPlayer,
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

    assert isinstance(player, NoNotificationSoundPlayer)


def test_windows_notification_sound_player_plays_bundled_mp3_with_mci(
    monkeypatch,
    tmp_path,
):
    sound_paths = {}
    for event_name in notifications.SOUND_EVENT_PATHS:
        sound_path = tmp_path / f"{event_name}.mp3"
        sound_path.write_bytes(b"mp3")
        sound_paths[event_name] = sound_path
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

    player = WindowsNotificationSoundPlayer(sound_paths)
    player.play_wake_word_detected()
    player.play_runner_started()
    player.play_runner_finished()
    player.play_application_error()
    player.play_speech_error()
    player.play_parse_error()
    player.play_click()

    assert commands == [
        "close keepclicking_notify_wake_word_detected",
        f'open "{sound_paths["wake_word_detected"]}" type mpegvideo alias keepclicking_notify_wake_word_detected',
        "play keepclicking_notify_wake_word_detected from 0",
        "close keepclicking_notify_runner_started",
        f'open "{sound_paths["runner_started"]}" type mpegvideo alias keepclicking_notify_runner_started',
        "play keepclicking_notify_runner_started from 0",
        "close keepclicking_notify_runner_finished",
        f'open "{sound_paths["runner_finished"]}" type mpegvideo alias keepclicking_notify_runner_finished',
        "play keepclicking_notify_runner_finished from 0",
        "close keepclicking_notify_application_error",
        f'open "{sound_paths["application_error"]}" type mpegvideo alias keepclicking_notify_application_error',
        "play keepclicking_notify_application_error from 0",
        "close keepclicking_notify_speech_error",
        f'open "{sound_paths["speech_error"]}" type mpegvideo alias keepclicking_notify_speech_error',
        "play keepclicking_notify_speech_error from 0",
        "close keepclicking_notify_parse_error",
        f'open "{sound_paths["parse_error"]}" type mpegvideo alias keepclicking_notify_parse_error',
        "play keepclicking_notify_parse_error from 0",
        "close keepclicking_notify_click",
        f'open "{sound_paths["click"]}" type mpegvideo alias keepclicking_notify_click',
        "play keepclicking_notify_click from 0",
    ]
