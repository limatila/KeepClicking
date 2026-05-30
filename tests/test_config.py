from src.core.config import InputMode, get_config


def test_get_config_defaults():
    config = get_config()
    assert config.input_mode == InputMode.SPEECH_OFFLINE
    assert config.move_pixels == 50
    assert config.scroll_units == 300
    assert config.pyautogui_pause_seconds == 0.1
    assert config.pyautogui_failsafe is True
    assert config.wake_word_phrase == "keeper"
    assert config.wake_word_listen_seconds == 5.0
    assert config.keyboard_prompt == "keepclicking> "
    assert config.offline_model_path is None


def test_get_config_overrides():
    base = get_config()
    updated = get_config(base, move_pixels=100)
    assert base.move_pixels == 50
    assert updated.move_pixels == 100
