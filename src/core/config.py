"""Application configuration defaults."""

from __future__ import annotations

from dataclasses import MISSING, dataclass, fields, replace
from pathlib import Path
from enum import Enum
from typing import Any, get_args, get_type_hints

from dotenv import dotenv_values

from src.core.choices import SpeechLanguage

ROOT_PATH = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_PATH / ".env"
MODELS_PATH = ROOT_PATH / "src" / "resources" / "models"

DEFAULT_OPENWAKEWORD_MODEL_PATH = (
    MODELS_PATH / "openwakeword" / "hey_keeper_v2.onnx"
)
DEFAULT_OFFLINE_MODEL_PATH = (
    MODELS_PATH / "vosk" / "vosk-model-small-en-us-0.15"
)


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Defines runtime configuration defaults for the MVP pipeline."""

    debug_mode: bool = False
    audio_input_device: str | None = None
    speech_language: SpeechLanguage = SpeechLanguage.EN_US
    
    openwakeword_model_path: str = str(DEFAULT_OPENWAKEWORD_MODEL_PATH)
    offline_model_path: str = str(DEFAULT_OFFLINE_MODEL_PATH)
    
    wake_word_phrase: str = "hey keeper"
    wake_word_listen_seconds: float = 3.0
    
    pyautogui_pause_seconds: float = 0.1
    pyautogui_failsafe: bool = True
    mouse_movement_pixels: int = 200
    mouse_scroll_units: int = 350
    

    @classmethod
    def from_env(cls) -> AppConfig:
        env_values = cls.read_env_values()
        field_types = get_type_hints(cls)
        
        parsed_values = {
            field_name: cls._parse_field_env_value(
                field_name, field_types[field_name], env_values, 
            )
            for field_name in field_types
        }
        
        return cls(**parsed_values)

    @staticmethod
    def read_env_values() -> dict[str, str | None]:
        return dict(dotenv_values(ENV_PATH))

    @staticmethod
    def _normalize_env_value(value: object) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @classmethod
    def _get_unwraped_optional_type(cls, annotation: Any) -> Any:
        non_none_args = [
            annotation_arg
            for annotation_arg in get_args(annotation)
            if annotation_arg is not type(None)
        ]
        
        if len(non_none_args) == 1:
            return non_none_args[0]
        
        return annotation

    @classmethod
    def _get_field_default(cls, field_name: str) -> Any:
        for config_field in fields(cls):
            if config_field.name != field_name:
                continue

            if config_field.default is not MISSING:
                return config_field.default
            if config_field.default_factory is not MISSING:
                return config_field.default_factory()

        raise AttributeError(f"Unrecognized config field '{field_name}' in env. Configurable are: {[f.name for f in fields(cls)]}")

    @classmethod
    def _parse_field_env_value(cls, field_name: str, annotation: Any, env_values: dict[str, str | None]) -> Any:
        
        def __parse_field_value_for_type(field_value: str, field_type, default_value):
            if field_type is str:
                return field_value

            if field_type is bool:
                if field_value.casefold() in {"1", "true"}:
                    return True
                if field_value.casefold() in {"0", "false"}:
                    return False

            if isinstance(field_type, type) and issubclass(field_type, Enum):
                normalized_enum_value = field_value.casefold().replace("-", "_")
                return field_type(normalized_enum_value)

            try:
                return field_type(field_value)    
            except:
                raise ValueError(
                    f"Failed to parse env value '{field_value}' for field '{field_name}' as type '{field_type.__name__}', please review your configurations."
                )
        
        default = cls._get_field_default(field_name)
        field_value = cls._normalize_env_value(env_values.get(field_name))
        
        if field_value is None:
            return default

        field_type = cls._get_unwraped_optional_type(annotation)
        return __parse_field_value_for_type(field_value, field_type, default)


DEBUG_MODE = AppConfig.from_env().debug_mode


def get_env_or_default(key: str, default: Any) -> Any:
    """Return a raw environment value when present, else the provided default."""
    env_values = AppConfig.read_env_values()
    return AppConfig._normalize_env_value(env_values.get(key)) or default


def get_config(base: AppConfig | None = None, **overrides: object) -> AppConfig:
    """Return the current config with optional overrides."""

    config = base or AppConfig.from_env()
    if overrides:
        return replace(config, **overrides)
    return config
