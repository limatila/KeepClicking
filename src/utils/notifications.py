"""Reusable notification sound helpers for KeepClicking."""

from __future__ import annotations

from pathlib import Path
import sys

from src.core.config import ASSETS_PATH
from src.core.logging import CORE_LOGGER


SOUND_EVENT_PATHS = {
    "wake_word_detected": ASSETS_PATH / "notify.mp3",
    "runner_started": ASSETS_PATH / "mouse-runner-start.mp3",
    "runner_finished": ASSETS_PATH / "finishing-loop.mp3",
    "application_error": ASSETS_PATH / "application-error.mp3",
    "speech_error": ASSETS_PATH / "speech-error.mp3",
    "parse_error": ASSETS_PATH / "parse-error.mp3",
    "click": ASSETS_PATH / "click.mp3",
}


class NotificationSoundPlayer:
    """Plays the user-facing notification sounds used across the app."""

    def play_wake_word_detected(self) -> None:
        """Play the wake-word detected notification sound."""

    def play_runner_started(self) -> None:
        """Play the runner startup notification sound."""

    def play_runner_finished(self) -> None:
        """Play the runner finished notification sound."""

    def play_application_error(self) -> None:
        """Play the application error notification sound."""

    def play_speech_error(self) -> None:
        """Play the speech recognition failure notification sound."""

    def play_parse_error(self) -> None:
        """Play the parse or validation failure notification sound."""

    def play_click(self) -> None:
        """Play the mouse click notification sound."""


class NoNotificationSoundPlayer(NotificationSoundPlayer):
    """Notification player for unsupported platforms."""


class WindowsNotificationSoundPlayer(NotificationSoundPlayer):
    """Windows notification player backed by MCI audio playback."""

    def __init__(self, sound_event_paths: dict[str, Path] | None = None) -> None:
        self.sound_event_paths = {
            event_name: Path(sound_path)
            for event_name, sound_path in (sound_event_paths or SOUND_EVENT_PATHS).items()
        }

    def play_wake_word_detected(self) -> None:
        self._play_sound_event("wake_word_detected")

    def play_runner_started(self) -> None:
        self._play_sound_event("runner_started")

    def play_runner_finished(self) -> None:
        self._play_sound_event("runner_finished")

    def play_application_error(self) -> None:
        self._play_sound_event("application_error")

    def play_speech_error(self) -> None:
        self._play_sound_event("speech_error")

    def play_parse_error(self) -> None:
        self._play_sound_event("parse_error")

    def play_click(self) -> None:
        self._play_sound_event("click")

    def _play_sound_event(self, event_name: str) -> None:
        try:
            sound_path = self.sound_event_paths.get(event_name)
            if sound_path is None:
                raise RuntimeError(f"Notification sound event is not configured: {event_name}")
            if not sound_path.exists():
                raise FileNotFoundError(f"Notification sound not found: {sound_path}")

            import ctypes

            alias = f"keepclicking_notify_{event_name}"
            self._mci_send_string(ctypes, f"close {alias}", ignore_errors=True)
            self._mci_send_string(
                ctypes,
                f'open "{sound_path}" type mpegvideo alias {alias}',
            )

            try:
                self._mci_send_string(ctypes, f"play {alias} from 0")
            except Exception:
                self._mci_send_string(ctypes, f"close {alias}", ignore_errors=True)
                raise
        
        except Exception as err:
            CORE_LOGGER.warning(f"Failed to play notification sound for event '{event_name}': {str(err)}",)

    def _mci_send_string(
        self,
        ctypes_module,
        command: str,
        ignore_errors: bool = False,
    ) -> None:
        winmm = ctypes_module.WinDLL("winmm")
        error_code = winmm.mciSendStringW(command, None, 0, None)

        if error_code == 0 or ignore_errors:
            return

        error_buffer = ctypes_module.create_unicode_buffer(256)
        winmm.mciGetErrorStringW(error_code, error_buffer, len(error_buffer))
        message = error_buffer.value or command

        raise RuntimeError(f"MCI notification sound command failed: {message}")


def build_notification_sound_player() -> NotificationSoundPlayer:
    """Return the best notification sound player for the current platform."""

    if sys.platform == "win32":
        return WindowsNotificationSoundPlayer()

    return NoNotificationSoundPlayer()
