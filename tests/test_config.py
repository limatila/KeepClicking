from pathlib import Path

from src.core.choices import SpeechLanguage
import src.core.config as config_module
from src.core.config import (
    DEFAULT_OFFLINE_MODEL_PATH,
    DEFAULT_OPENWAKEWORD_MODEL_PATH,
    AppConfig,
    get_config,
)


def test_default_runtime_dir_uses_appdata_on_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "AppData" / "Roaming"))

    assert config_module.AppConfig._default_runtime_dir() == (
        tmp_path / "AppData" / "Roaming" / "KeepClicking"
    )


def test_default_runtime_dir_uses_xdg_data_home_on_linux(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "share"))

    assert config_module.AppConfig._default_runtime_dir() == tmp_path / "share" / "KeepClicking"


def test_default_runtime_dir_falls_back_to_local_share_on_linux(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module.sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(config_module.Path, "home", staticmethod(lambda: tmp_path / "home"))

    assert config_module.AppConfig._default_runtime_dir() == (
        tmp_path / "home" / ".local" / "share" / "KeepClicking"
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


def test_get_config_reads_explicit_source_env_path(tmp_path, monkeypatch):
    runtime_dir = tmp_path / "runtime"
    local_env_path = tmp_path / ".env"
    local_env_path.write_text(
        "\n".join(
            (
                "mouse_movement_pixels=777",
                "offline_model_path=models/dev-vosk",
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module.AppConfig, "_default_runtime_dir", lambda: runtime_dir)

    config = get_config(
        source_env_path=local_env_path,
        seed_user_env=False,
    )

    assert config.mouse_movement_pixels == 777
    assert config.env_path == local_env_path.resolve()
    assert Path(config.offline_model_path) == (
        tmp_path / "models" / "dev-vosk"
    ).resolve()
    assert not (runtime_dir / ".env").exists()


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
            "wake_word_notification": "false",
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
        wake_word_notification=False,
        audio_input_device="USB 2.0",
        speech_language=SpeechLanguage.PT_BR,
    )


def test_read_env_values_uses_the_single_user_env_path(tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundle"
    runtime_dir = tmp_path / "runtime"
    bundle_dir.mkdir()
    runtime_dir.mkdir()

    (bundle_dir / "packaged.env").write_text(
        "\n".join(
            (
                "speech_language=en_us",
                "offline_model_path=src/resources/models/vosk/vosk-model-small-en-us-0.15",
                "mouse_movement_pixels=200",
            )
        ),
        encoding="utf-8",
    )
    (runtime_dir / ".env").write_text(
        "\n".join(
            (
                "speech_language=pt-br",
                "mouse_movement_pixels=275",
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "ROOT_PATH", bundle_dir)
    monkeypatch.setattr(config_module.AppConfig, "_default_runtime_dir", lambda: runtime_dir)

    env_values = AppConfig.read_env_values()

    assert env_values["speech_language"] == "pt-br"
    assert env_values["mouse_movement_pixels"] == "275"
    assert Path(env_values["offline_model_path"]) == (
        bundle_dir
        / "src"
        / "resources"
        / "models"
        / "vosk"
        / "vosk-model-small-en-us-0.15"
    ).resolve()


def test_read_env_values_seeds_user_env_from_bundled_defaults(tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    (bundle_dir / "packaged.env").write_text(
        "\n".join(
            (
                "debug_mode=false",
                "mouse_movement_pixels=350",
                "offline_model_path=src/resources/models/vosk/vosk-model-small-en-us-0.15",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    runtime_dir = tmp_path / "runtime"
    monkeypatch.setattr(config_module, "ROOT_PATH", bundle_dir)
    monkeypatch.setattr(config_module.AppConfig, "_default_runtime_dir", lambda: runtime_dir)

    env_values = AppConfig.read_env_values()

    assert (runtime_dir / ".env").read_text(encoding="utf-8") == (
        "debug_mode=false\nmouse_movement_pixels=350\n"
    )
    assert Path(env_values["offline_model_path"]) == (
        bundle_dir
        / "src"
        / "resources"
        / "models"
        / "vosk"
        / "vosk-model-small-en-us-0.15"
    ).resolve()


def test_read_env_values_resolves_user_relative_path_overrides_from_runtime_dir(tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundle"
    runtime_dir = tmp_path / "runtime"
    bundle_dir.mkdir()
    runtime_dir.mkdir()

    (bundle_dir / "packaged.env").write_text(
        "offline_model_path=src/resources/models/vosk/default-model\n",
        encoding="utf-8",
    )
    (runtime_dir / ".env").write_text(
        "offline_model_path=models/custom-vosk\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "ROOT_PATH", bundle_dir)
    monkeypatch.setattr(config_module.AppConfig, "_default_runtime_dir", lambda: runtime_dir)

    env_values = AppConfig.read_env_values()

    assert Path(env_values["offline_model_path"]) == (
        runtime_dir / "models" / "custom-vosk"
    ).resolve()
