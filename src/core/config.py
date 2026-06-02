"""Application configuration defaults."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from dotenv import get_key

ENV_PATH = ".env"


def get_env_or_default(key: str, default: str) -> str:
    """Helper to get environment variable (by key) or fallback to default."""
    key_result = get_key(ENV_PATH, key)

    if key_result is None:
        key_result = default
    
    return key_result


class InputMode(str, Enum):
    """Enumerates supported input modes for the MVP pipeline."""

    SPEECH_OFFLINE = "speech_offline"
    KEYBOARD_DEV = "keyboard_dev"


@dataclass(frozen=True)
class AppConfig:
    """Defines runtime configuration defaults for the MVP pipeline."""

    pyautogui_pause_seconds: float = get_env_or_default('pyautogui_pause_seconds', 0.1)
    pyautogui_failsafe: bool = get_env_or_default('pyautogui_failsafe', True)
    
    input_mode: InputMode = get_env_or_default('input_mode', InputMode.SPEECH_OFFLINE)
    mouse_movement_pixels: int = get_env_or_default('mouse_movement_pixels', 50)
    mouse_scroll_units: int = get_env_or_default('mouse_scroll_units', 300)
    
    keyboard_prompt: str = get_env_or_default('keyboard_prompt', "keepclicking> ")
    
    offline_model_path: str | None = get_env_or_default('offline_model_path', None)
    wake_word_phrase: str = get_env_or_default('wake_word_phrase', "keeper")
    wake_word_listen_seconds: float = get_env_or_default('wake_word_listen_seconds', 5.0)


def get_config(base: AppConfig | None = AppConfig(), **overrides: object) -> AppConfig:
    """Return a copy of the config with overrides if present."""

    if overrides:
        return replace(base, **overrides)
    else:
        return base
