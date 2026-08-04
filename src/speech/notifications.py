"""User notification helpers for speech interactions."""

from __future__ import annotations

import sys
from typing import Protocol


class NotificationSoundPlayer(Protocol):
    """Plays a short user-facing notification sound."""

    def play_wake_word_detected(self) -> None:
        """Play the wake-word detected notification sound."""


class NoOpNotificationSoundPlayer:
    """Notification player for platforms without a supported sound backend."""

    def play_wake_word_detected(self) -> None:
        return None


class WindowsNotificationSoundPlayer:
    """Windows notification player using the user's configured system sounds."""

    def play_wake_word_detected(self) -> None:
        import winsound

        winsound.MessageBeep(winsound.MB_ICONASTERISK)


def build_notification_sound_player() -> NotificationSoundPlayer:
    """Return the best notification sound player for the current platform."""

    if sys.platform == "win32":
        return WindowsNotificationSoundPlayer()

    return NoOpNotificationSoundPlayer()
