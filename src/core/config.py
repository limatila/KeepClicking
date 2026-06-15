"""Application configuration defaults."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from dotenv import get_key

ROOT_PATH = Path(__file__).parent.parent.parent
ENV_PATH = ".env"
MODELS_PATH = ROOT_PATH / "src" / "speech" / "wakeword" / "models"


def get_env_or_default(key: str, default: str) -> str:
    """Helper to get environment variable (by key) or fallback to default."""
    key_result = get_key(ENV_PATH, key)

    if key_result is None:
        key_result = default
    
    return key_result


DEBUG_MODE = get_env_or_default('debug_mode', 'False').title() == 'True'


@dataclass(frozen=True)
class AppConfig:
    """Defines runtime configuration defaults for the MVP pipeline."""

    debug_mode: bool = DEBUG_MODE

    openwakeword_model_path: str = get_env_or_default('openwakeword_model_path', MODELS_PATH / "keeper_v1.onnx")
    pyautogui_pause_seconds: float = get_env_or_default('pyautogui_pause_seconds', 0.1)
    pyautogui_failsafe: bool | None = get_key(ENV_PATH, 'pyautogui_failsafe')
    
    mouse_movement_pixels: int = get_env_or_default('mouse_movement_pixels', 50)
    mouse_scroll_units: int = get_env_or_default('mouse_scroll_units', 300)
    
    keyboard_prompt: str = get_env_or_default('keyboard_prompt', "keepclicking> ")
    
    offline_model_path: str | None = get_env_or_default('offline_model_path', None)
    wake_word_phrase: str = get_env_or_default('wake_word_phrase', "keeper")
    wake_word_listen_seconds: float = get_env_or_default('wake_word_listen_seconds', 5.0)
    audio_input_device: str | None = get_key(ENV_PATH, 'audio_input_device') #* Can be name or specific index

    def __post_init__(self):
        if self.debug_mode and not self.pyautogui_failsafe:
            object.__setattr__(self, 'pyautogui_failsafe', self.debug_mode)


def get_config(base: AppConfig | None = AppConfig(), **overrides: object) -> AppConfig:
    """Return a copy of the config with overrides if present."""

    if overrides:
        return replace(base, **overrides)
    else:
        return base
