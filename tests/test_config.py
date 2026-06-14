from src.core.config import AppConfig, get_config


def test_get_config_defaults():
    config = get_config()
    assert config.mouse_movement_pixels == 50
    assert config.mouse_scroll_units == 300
    assert config.pyautogui_pause_seconds == 0.1
    assert config.pyautogui_failsafe is True
    assert config.wake_word_phrase == "keeper"
    assert config.wake_word_listen_seconds == 5.0 
    assert config.keyboard_prompt == "keepclicking> "
    assert config.offline_model_path is None


def test_get_config_overrides():
    base = get_config()
    updated = get_config(base, mouse_movement_pixels=100)
    assert base.mouse_movement_pixels == 50
    assert updated.mouse_movement_pixels == 100


def test_get_config_allows_unset_audio_input_device():
    config = get_config(audio_input_device=None)

    assert config.audio_input_device is None
