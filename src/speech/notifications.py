"""User notification helpers for speech interactions."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Protocol

from src.core.config import DEFAULT_NOTIFICATION_SOUND_PATH


class NotificationSoundPlayer(Protocol):
    """Plays a short user-facing notification sound."""

    def play_wake_word_detected(self) -> None:
        """Play the wake-word detected notification sound."""


class NoOpNotificationSoundPlayer:
    """Notification player for platforms without a supported sound backend."""

    def play_wake_word_detected(self) -> None:
        return None


class WindowsNotificationSoundPlayer:
    """Notification player using the wake-word sound asset."""

    def __init__(self, sound_path: Path = DEFAULT_NOTIFICATION_SOUND_PATH) -> None:
        self.sound_path = Path(sound_path)

    def play_wake_word_detected(self) -> None:
        if not self.sound_path.exists():
            raise FileNotFoundError(f"Notification sound not found: {self.sound_path}")

        import ctypes

        alias = "keepclicking_notify"
        self._mci_send_string(ctypes, f"close {alias}", ignore_errors=True)
        self._mci_send_string(
            ctypes,
            f'open "{self.sound_path}" type mpegvideo alias {alias}',
        )
        
        try:
            self._mci_send_string(ctypes, f"play {alias} from 0")
        
        except Exception:
            self._mci_send_string(ctypes, f"close {alias}", ignore_errors=True)
            raise

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

    return NoOpNotificationSoundPlayer()
