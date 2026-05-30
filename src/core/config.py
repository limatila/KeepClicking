"""Application configuration defaults."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class InputMode(str, Enum):
    """Enumerates supported input modes for the MVP pipeline."""

    SPEECH_OFFLINE = "speech_offline"
    KEYBOARD_DEV = "keyboard_dev"


@dataclass(frozen=True)
class AppConfig:
    """Defines runtime configuration defaults for the MVP pipeline."""

    input_mode: InputMode = InputMode.SPEECH_OFFLINE
    move_pixels: int = 50
    scroll_units: int = 300
    pyautogui_pause_seconds: float = 0.1
    pyautogui_failsafe: bool = True
    wake_word_phrase: str = "keeper"
    wake_word_listen_seconds: float = 5.0
    keyboard_prompt: str = "keepclicking> "
    offline_model_path: str | None = None


def get_config(base: AppConfig | None = None, **overrides: object) -> AppConfig:
	"""Return a copy of the config with overrides applied."""

	if base is None:
		return AppConfig()

	return replace(base, **overrides)
