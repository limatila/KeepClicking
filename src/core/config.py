"""Application configuration and centralized runtime paths."""

from __future__ import annotations

import sys
import os
from dataclasses import MISSING, dataclass, field, fields, replace
from enum import Enum
from pathlib import Path
from typing import Any, get_args, get_type_hints

import openwakeword
from dotenv import dotenv_values

from src.core.choices import SpeechLanguage

ROOT_PATH = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))

BUNDLED_ENV_FILE_NAME = "packaged.env"
BUNDLED_ENV_PATH = ROOT_PATH / BUNDLED_ENV_FILE_NAME

MODELS_PATH = ROOT_PATH / "src" / "resources" / "models"
ASSETS_PATH = ROOT_PATH / "src" / "resources" / "assets"

OPENWAKEWORD_PACKAGED_MODEL_DIR = MODELS_PATH / "openwakeword"
OPENWAKEWORD_LIB_MODEL_DIR = (
    Path(openwakeword.__file__).resolve().parent / "resources" / "models"
)

DEFAULT_OPENWAKEWORD_MODEL_PATH = (
    OPENWAKEWORD_PACKAGED_MODEL_DIR / "hey_keeper_v2.onnx"
)
DEFAULT_OFFLINE_MODEL_PATHS = {
    SpeechLanguage.EN_US: MODELS_PATH / "vosk" / "vosk-model-small-en-us-0.15",
    SpeechLanguage.PT_BR: MODELS_PATH / "vosk" / "vosk-model-small-pt-0.3",
}
DEFAULT_OFFLINE_MODEL_PATH = DEFAULT_OFFLINE_MODEL_PATHS[SpeechLanguage.EN_US]
DEFAULT_NOTIFICATION_SOUND_PATH = ASSETS_PATH / "notify.mp3"
DEFAULT_LOG_FORMAT = "[%(levelname)s] | %(name)s -|- %(message)s"
PATH_ENV_FIELDS = frozenset({"openwakeword_model_path", "offline_model_path"})


def get_default_offline_model_path(language: SpeechLanguage) -> Path:
    """Return the bundled Vosk model directory for the configured language."""

    return DEFAULT_OFFLINE_MODEL_PATHS[language]


@dataclass(slots=True)
class AppConfig:
    """Defines runtime configuration defaults and the application runtime root."""

    # Env Configurations
    debug_mode: bool = False
    audio_input_device: str | None = None
    speech_language: SpeechLanguage = SpeechLanguage.EN_US
    openwakeword_model_path: str = str(DEFAULT_OPENWAKEWORD_MODEL_PATH)
    offline_model_path: str | None = None
    wake_word_phrase: str = "hey keeper"
    wake_word_notification: bool = True
    wake_word_listen_seconds: float = 3.0
    pyautogui_pause_seconds: float = 0.1
    pyautogui_failsafe: bool = True
    mouse_movement_pixels: int = 200
    mouse_scroll_units: int = 350
    logging_format: str = DEFAULT_LOG_FORMAT

    # Management Dir Paths
    @staticmethod
    def _default_runtime_dir() -> Path:
        """
        Return the durable, per-user application root for this platform.

        - Windows: %APPDATA%\\KeepClicking
        - Linux: $XDG_DATA_HOME/KeepClicking or ~/.local/share/KeepClicking
        """
        if sys.platform == "win32":
            app_data = os.environ.get("APPDATA")
            
            if app_data:
                return Path(app_data) / "KeepClicking"
            
            return Path.home() / "AppData" / "Roaming" / "KeepClicking"
        
        if sys.platform == "linux":
            data_home = os.environ.get("XDG_DATA_HOME")
            
            if data_home:
                return Path(data_home) / "KeepClicking"
            
            return Path.home() / ".local" / "share" / "KeepClicking"

        raise NotImplementedError(f"Unsupported platform '{sys.platform}' for runtime dir.")

    runtime_dir: Path = field(default_factory=_default_runtime_dir)
    env_path: Path = None
    log_dir: Path = None
    openwakeword_cache_dir: Path = None

    def __post_init__(self) -> None:
        if not self.offline_model_path:
            self.offline_model_path = str(
                get_default_offline_model_path(self.speech_language)
            )

        runtime_dir = Path(self.runtime_dir).resolve()
        env_path = Path(self.env_path).resolve() if self.env_path else runtime_dir / ".env"
        log_dir = runtime_dir / "logs"
        cache_dir = runtime_dir / ".cache" / "models" / "openwakeword"

        runtime_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)

        self.runtime_dir = runtime_dir
        self.env_path = env_path
        self.log_dir = log_dir
        self.openwakeword_cache_dir = cache_dir

    @classmethod
    def appdata_runtime_dir(cls, runtime_dir: Path | None = None) -> Path:
        """Create and return the one application-managed runtime root."""
        root = Path(runtime_dir or cls._default_runtime_dir()).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root

    def display(self):
        """Display text of the current configuration to stdout."""
        display_text = "\n"
        
        display_text += ("Runtime Active Configuration:") + " | "
        
        display_text += (f"Runtime Dir: {self.runtime_dir}") + " | "
        display_text += (f"Env Path: {self.env_path}") + " | "
        display_text += (f"Log Dir: {self.log_dir}") + " | "
        
        display_text += (f"OpenWakeWord Cache Dir: {self.openwakeword_cache_dir}") + " | "
        
        display_text += ("Configuration Values= ")
        for config_field in fields(self):
            if config_field.name.startswith("_"):
                continue
            value = getattr(self, config_field.name)
            display_text += (f"{config_field.name}: {value}") + " | "
        
        return display_text

    @classmethod
    def from_env(
        cls,
        source_env_path: Path | None = None,
        seed_user_env: bool = True,
    ) -> AppConfig:
        if source_env_path is None and seed_user_env:
            env_values = cls.read_env_values()
        else:
            env_values = cls.read_env_values(
                source_env_path=source_env_path,
                seed_user_env=seed_user_env,
            )

        field_types = get_type_hints(cls)
        parsed_values = {
            config_field.name: cls._parse_field_env_value(
                config_field.name, field_types[config_field.name], env_values
            )
            for config_field in fields(cls)
            if config_field.init and config_field.name != "runtime_dir"
        }
        if source_env_path is not None:
            parsed_values["env_path"] = Path(source_env_path).resolve()

        return cls(**parsed_values)

    @classmethod
    def read_env_values(
        cls,
        source_env_path: Path | None = None,
        seed_user_env: bool = True,
    ) -> dict[str, str | None]:
        runtime_dir = cls.appdata_runtime_dir()
        user_env_path = (
            Path(source_env_path).resolve()
            if source_env_path is not None
            else runtime_dir / ".env"
        )
        bundled_env_path = ROOT_PATH / BUNDLED_ENV_FILE_NAME

        if seed_user_env and not user_env_path.exists():
            cls._seed_user_env_file(user_env_path, bundled_env_path)

        merged_env_values: dict[str, str | None] = {}
        for env_values, base_dir in (
            (cls._read_env_file(bundled_env_path), bundled_env_path.parent),
            (cls._read_env_file(user_env_path), user_env_path.parent),
        ):
            merged_env_values.update(
                cls._resolve_env_path_fields(env_values, base_dir)
            )

        return merged_env_values

    @classmethod
    def _read_env_file(cls, env_path: Path) -> dict[str, str | None]:
        if not env_path.exists():
            return {}

        return dict(dotenv_values(env_path))

    @classmethod
    def _seed_user_env_file(cls, user_env_path: Path, bundled_env_path: Path) -> None:
        seeded_lines: list[str] = []
        for field_name, raw_value in cls._read_env_file(bundled_env_path).items():
            if field_name in PATH_ENV_FIELDS:
                continue

            normalized_value = cls._normalize_env_value(raw_value)
            if normalized_value is None:
                continue

            seeded_lines.append(f"{field_name}={normalized_value}")

        user_env_path.write_text(
            "\n".join(seeded_lines) + ("\n" if seeded_lines else ""),
            encoding="utf-8",
        )

    @staticmethod
    def _normalize_env_value(value: object) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @classmethod
    def _resolve_env_path_fields(cls, env_values: dict[str, str | None], base_dir: Path) -> dict[str, str | None]:
        resolved_env_values = dict(env_values)

        for field_name in PATH_ENV_FIELDS:
            raw_value = cls._normalize_env_value(resolved_env_values.get(field_name))
            
            if raw_value is None:
                continue
            
            candidate_path = Path(raw_value)
            if not candidate_path.is_absolute():
                candidate_path = (base_dir / candidate_path).resolve()
            
            resolved_env_values[field_name] = str(candidate_path)
        
        return resolved_env_values

    @classmethod
    def _get_unwraped_optional_type(cls, annotation: Any) -> Any:
        non_none_args = [annotation_arg for annotation_arg in get_args(annotation) if annotation_arg is not type(None)]
        return non_none_args[0] if len(non_none_args) == 1 else annotation

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

def get_config(
    base: AppConfig | None = None,
    source_env_path: Path | None = None,
    seed_user_env: bool = True,
    **overrides: object,
) -> AppConfig:
    """Return the current config with optional overrides."""
    config = base or AppConfig.from_env(
        source_env_path=source_env_path,
        seed_user_env=seed_user_env,
    )
    
    if overrides:
        if "speech_language" in overrides and "offline_model_path" not in overrides:
            next_language = overrides["speech_language"]
            if (
                isinstance(next_language, SpeechLanguage) and
                config.offline_model_path == str(get_default_offline_model_path(config.speech_language))
            ):
                overrides["offline_model_path"] = str(
                    get_default_offline_model_path(next_language)
                )

        return replace(config, **overrides)

    return config
