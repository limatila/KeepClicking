from pathlib import Path

import src.core.config as config_module
from src.core.config import (
    DEFAULT_OFFLINE_MODEL_PATH,
    DEFAULT_OPENWAKEWORD_MODEL_PATH,
    AppConfig,
    get_config,
)


def test_get_config_defaults():
    config = get_config()
    assert config.mouse_movement_pixels == 50
    assert config.mouse_scroll_units == 300
    assert config.pyautogui_pause_seconds == 0.1
    assert config.pyautogui_failsafe is True
    assert config.wake_word_phrase == "keeper"
    assert config.wake_word_listen_seconds == 5.0
    assert config.keyboard_prompt == "keepclicking> "
    assert Path(config.offline_model_path) == DEFAULT_OFFLINE_MODEL_PATH
    assert Path(config.openwakeword_model_path) == DEFAULT_OPENWAKEWORD_MODEL_PATH


def test_get_config_overrides():
    base = get_config()
    updated = get_config(base, mouse_movement_pixels=100)
    assert base.mouse_movement_pixels == 50
    assert updated.mouse_movement_pixels == 100


def test_get_config_allows_unset_audio_input_device():
    config = get_config(audio_input_device=None)

    assert config.audio_input_device is None


def test_get_config_parses_env_values(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "_read_env_values",
        lambda: {
            "debug_mode": "true",
            "pyautogui_pause_seconds": "0.25",
            "pyautogui_failsafe": "false",
            "mouse_movement_pixels": "75",
            "mouse_scroll_units": "425",
            "wake_word_listen_seconds": "2.5",
            "audio_input_device": "USB 2.0",
        },
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
        keyboard_prompt="keepclicking> ",
        wake_word_phrase="keeper",
        wake_word_listen_seconds=2.5,
        audio_input_device="USB 2.0",
    )
