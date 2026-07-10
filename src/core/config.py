"""Application configuration defaults."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

ROOT_PATH = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_PATH / ".env"
MODELS_PATH = ROOT_PATH / "src" / "resources" / "models"

DEFAULT_OPENWAKEWORD_MODEL_PATH = (
    MODELS_PATH / "openwakeword" / "keeper_v1.onnx"
)
DEFAULT_OFFLINE_MODEL_PATH = (
    MODELS_PATH / "vosk" / "vosk-model-small-en-us-0.15"
)


@dataclass(frozen=True)
class AppConfig:
    """Defines runtime configuration defaults for the MVP pipeline."""

    debug_mode: bool = False
    openwakeword_model_path: str = str(DEFAULT_OPENWAKEWORD_MODEL_PATH)
    offline_model_path: str = str(DEFAULT_OFFLINE_MODEL_PATH)
    pyautogui_pause_seconds: float = 0.1
    pyautogui_failsafe: bool = True
    mouse_movement_pixels: int = 50
    mouse_scroll_units: int = 300
    keyboard_prompt: str = "keepclicking> "
    wake_word_phrase: str = "keeper"
    wake_word_listen_seconds: float = 5.0
    audio_input_device: str | None = None

    @staticmethod
    def _read_env_values() -> dict[str, str | None]:
        return dict(dotenv_values(ENV_PATH))

    @staticmethod
    def _normalize_env_value(value: object) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @classmethod
    def _get_env_value(
        cls,
        key: str,
        env_values: dict[str, str | None],
    ) -> str | None:
        return cls._normalize_env_value(env_values.get(key))

    @classmethod
    def _parse_bool(
        cls,
        key: str,
        default: bool,
        env_values: dict[str, str | None],
    ) -> bool:
        value = cls._get_env_value(key, env_values)
        if value is None:
            return default
        if value.casefold() in {"1", "true"}:
            return True
        if value.casefold() in {"0", "false"}:
            return False
        return default

    @classmethod
    def _parse_int(
        cls,
        key: str,
        default: int,
        env_values: dict[str, str | None],
    ) -> int:
        value = cls._get_env_value(key, env_values)
        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            return default

    @classmethod
    def _parse_float(
        cls,
        key: str,
        default: float,
        env_values: dict[str, str | None],
    ) -> float:
        value = cls._get_env_value(key, env_values)
        if value is None:
            return default

        try:
            return float(value)
        except ValueError:
            return default

    @classmethod
    def _parse_str(
        cls,
        key: str,
        default: str,
        env_values: dict[str, str | None],
    ) -> str:
        return cls._get_env_value(key, env_values) or default

    @classmethod
    def from_env(cls) -> AppConfig:
        env_values = cls._read_env_values()
        return cls(
            debug_mode=cls._parse_bool("debug_mode", False, env_values),
            openwakeword_model_path=cls._parse_str(
                "openwakeword_model_path",
                str(DEFAULT_OPENWAKEWORD_MODEL_PATH),
                env_values,
            ),
            offline_model_path=cls._parse_str(
                "offline_model_path",
                str(DEFAULT_OFFLINE_MODEL_PATH),
                env_values,
            ),
            pyautogui_pause_seconds=cls._parse_float(
                "pyautogui_pause_seconds",
                0.1,
                env_values,
            ),
            pyautogui_failsafe=cls._parse_bool(
                "pyautogui_failsafe",
                True,
                env_values,
            ),
            mouse_movement_pixels=cls._parse_int(
                "mouse_movement_pixels",
                50,
                env_values,
            ),
            mouse_scroll_units=cls._parse_int(
                "mouse_scroll_units",
                300,
                env_values,
            ),
            keyboard_prompt=cls._parse_str(
                "keyboard_prompt",
                "keepclicking> ",
                env_values,
            ),
            wake_word_phrase=cls._parse_str(
                "wake_word_phrase",
                "keeper",
                env_values,
            ),
            wake_word_listen_seconds=cls._parse_float(
                "wake_word_listen_seconds",
                5.0,
                env_values,
            ),
            audio_input_device=cls._get_env_value(
                "audio_input_device",
                env_values,
            ),
        )


DEBUG_MODE = AppConfig.from_env().debug_mode


def get_env_or_default(key: str, default: Any) -> Any:
    """Return a raw environment value when present, else the provided default."""
    env_values = AppConfig._read_env_values()
    return AppConfig._get_env_value(key, env_values) or default


def get_config(base: AppConfig | None = None, **overrides: object) -> AppConfig:
    """Return the current config with optional overrides."""

    config = base or AppConfig.from_env()
    if overrides:
        return replace(config, **overrides)
    return config
