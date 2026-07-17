from pathlib import Path

from src.core.choices import SpeechLanguage
import src.core.config as config_module
from src.core.config import (
    DEFAULT_OFFLINE_MODEL_PATH,
    DEFAULT_OPENWAKEWORD_MODEL_PATH,
    AppConfig,
    get_config,
)


def test_get_config_defaults(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {}),
    )
    config = get_config()
    assert config.pyautogui_failsafe is True
    assert "keeper" in config.wake_word_phrase
    assert Path(config.offline_model_path) == DEFAULT_OFFLINE_MODEL_PATH
    assert Path(config.openwakeword_model_path) == DEFAULT_OPENWAKEWORD_MODEL_PATH
    assert config.speech_language == SpeechLanguage.EN_US


def test_get_config_overrides():
    base = get_config()
    updated = get_config(base, mouse_movement_pixels=123)
    assert updated.mouse_movement_pixels == 123


def test_get_config_allows_unset_audio_input_device():
    config = get_config(audio_input_device=None)

    assert config.audio_input_device is None


def test_get_config_parses_env_values(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {
            "debug_mode": "true",
            "pyautogui_pause_seconds": "0.25",
            "pyautogui_failsafe": "false",
            "mouse_movement_pixels": "75",
            "mouse_scroll_units": "425",
            "wake_word_listen_seconds": "2.5",
            "audio_input_device": "USB 2.0",
            "speech_language": "pt-br",
        }),
    )

    config = get_config()

    assert config == AppConfig(
        debug_mode=True,
        openwakeword_model_path=str(DEFAULT_OPENWAKEWORD_MODEL_PATH),
        offline_model_path=str(DEFAULT_OFFLINE_MODEL_PATH),
        pyautogui_pause_seconds=0.25,
        pyautogui_failsafe=False,
        mouse_movement_pixels=75,
        mouse_scroll_units=425,
        wake_word_listen_seconds=2.5,
        audio_input_device="USB 2.0",
        speech_language=SpeechLanguage.PT_BR,
    )
