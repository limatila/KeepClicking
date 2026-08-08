import logging
import numpy as np
import pytest
from pathlib import Path

from src.core.config import get_config
from src.core.errors import AdapterError
from src.speech.audio_device_resolver import AudioDeviceResolver
import src.speech.wakeword.engine as wakeword_engine
from src.speech.wakeword.engine import OpenWakeWordEngine


class FakeNotificationSoundPlayer:
    def __init__(self, error: Exception | None = None):
        self.calls = 0
        self.error = error

    def play_wake_word_detected(self) -> None:
        self.calls += 1
        if self.error is not None:
            raise self.error


def test_load_model_uses_configured_model_path(monkeypatch):
    created_models = []
    config = get_config(
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )

    class FakeModel:
        def __init__(self, *args, **kwargs):
            created_models.append((args, kwargs))

    monkeypatch.setattr(wakeword_engine, "Model", FakeModel)
    monkeypatch.setattr(
        wakeword_engine.os.path,
        "exists",
        lambda path: path == config.openwakeword_model_path,
    )

    engine = OpenWakeWordEngine(config)
    monkeypatch.setattr(
        engine,
        "_resolve_openwakeword_feature_models",
        lambda: ("/tmp/melspectrogram.onnx", "/tmp/embedding_model.onnx"),
    )
    model = engine.load_model()

    assert isinstance(model, FakeModel)
    assert created_models == [
        (
            (),
            {
                "wakeword_models": [config.openwakeword_model_path],
                "inference_framework": "onnx",
                "melspec_model_path": "/tmp/melspectrogram.onnx",
                "embedding_model_path": "/tmp/embedding_model.onnx",
            },
        )
    ]


def test_load_model_logs_effective_model_and_support_assets(monkeypatch, caplog):
    created_models = []
    config = get_config(
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )

    class FakeModel:
        def __init__(self, *args, **kwargs):
            created_models.append((args, kwargs))

    monkeypatch.setattr(wakeword_engine, "Model", FakeModel)
    monkeypatch.setattr(
        wakeword_engine.os.path,
        "exists",
        lambda path: path == config.openwakeword_model_path,
    )

    engine = OpenWakeWordEngine(config)
    monkeypatch.setattr(
        engine,
        "_resolve_openwakeword_feature_models",
        lambda: ("/tmp/melspectrogram.onnx", "/tmp/embedding_model.onnx"),
    )

    with caplog.at_level(logging.INFO, logger="baseLogger.adapter"):
        engine.load_model()

    assert created_models
    assert any(
        "Loading wake-word model from '/tmp/custom_wakeword.onnx'" in record.message
        and "/tmp/melspectrogram.onnx" in record.message
        and "/tmp/embedding_model.onnx" in record.message
        for record in caplog.records
    )


def test_resolve_openwakeword_feature_models_downloads_missing_assets(
    monkeypatch,
    tmp_path,
):
    package_root = tmp_path / "package"
    package_root.mkdir()
    created_downloads = []

    class FakeOpenWakeWord:
        __file__ = str(package_root / "__init__.py")
        FEATURE_MODELS = {
            "melspectrogram": {
                "download_url": "https://example.invalid/melspectrogram.tflite"
            },
            "embedding": {
                "download_url": "https://example.invalid/embedding_model.tflite"
            },
        }

    def fake_download(url, target_directory):
        created_downloads.append((url, target_directory))
        Path(target_directory, url.rsplit("/", 1)[-1]).write_bytes(b"model")

    monkeypatch.setattr(wakeword_engine, "openwakeword", FakeOpenWakeWord)
    monkeypatch.setattr(wakeword_engine, "OPENWAKEWORD_PACKAGED_MODEL_DIR", package_root / "resources" / "models")
    monkeypatch.setattr(wakeword_engine, "OPENWAKEWORD_LIB_MODEL_DIR", package_root / "library-models")
    monkeypatch.setattr(wakeword_engine, "download_file", fake_download)

    engine = OpenWakeWordEngine(get_config(audio_input_device=None, runtime_dir=tmp_path / "runtime"))
    melspec_path, embedding_path = engine._resolve_openwakeword_feature_models()

    cache_dir = engine.config.openwakeword_cache_dir
    assert Path(melspec_path) == cache_dir / "melspectrogram.onnx"
    assert Path(embedding_path) == cache_dir / "embedding_model.onnx"
    assert created_downloads == [
        ("https://example.invalid/melspectrogram.onnx", str(cache_dir)),
        ("https://example.invalid/embedding_model.onnx", str(cache_dir)),
    ]


def test_prepare_model_audio_frame_converts_float32_to_int16():
    engine = OpenWakeWordEngine(get_config(audio_input_device=None))

    audio = np.array([[-1.2], [0.0], [1.2]], dtype=np.float32)

    prepared = engine._prepare_model_audio_frame(audio)

    assert prepared.dtype == np.int16
    assert prepared.shape == (3,)
    assert prepared.tolist() == [-32767, 0, 32767]


def test_score_frame_returns_max_score_from_dict():
    engine = OpenWakeWordEngine(get_config(audio_input_device=None))

    class FakeModel:
        def predict(self, audio_frame):
            return {"keeper": 0.1, "hey_keeper_v2": 0.8}

    score = engine.score_frame(FakeModel(), np.zeros(1280, dtype=np.int16))

    assert score == 0.8


def test_raise_if_instant_audio_read_rejects_too_fast_reads():
    engine = OpenWakeWordEngine(
        get_config(audio_input_device=None),
        chunk_seconds=0.5,
    )

    with pytest.raises(AdapterError, match="returned too quickly"):
        engine._raise_if_instant_audio_read(0.1)


def test_raise_if_instant_audio_read_allows_normal_reads():
    engine = OpenWakeWordEngine(
        get_config(audio_input_device=None),
        chunk_seconds=0.5,
    )

    engine._raise_if_instant_audio_read(0.101)


def test_wait_for_wake_word_reuses_one_input_stream(monkeypatch):
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )

    class FakeModel:
        def __init__(self):
            self.calls = 0
            self.audio_frames = []

        def predict(self, audio_frame):
            self.calls += 1
            self.audio_frames.append(audio_frame.copy())
            return 0.1 if self.calls == 1 else 0.9

    class FakeInputStream:
        instances = 0
        read_calls = 0

        def __init__(self, *args, **kwargs):
            FakeInputStream.instances += 1
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            FakeInputStream.read_calls += 1
            assert frames == self.blocksize
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert FakeInputStream.instances == 1
    assert FakeInputStream.read_calls == 2


def test_wait_for_wake_word_plays_notification_sound_on_detection(monkeypatch):
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )
    notification_sound_player = FakeNotificationSoundPlayer()
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )
    engine.notification_sound_player = notification_sound_player

    class FakeModel:
        def predict(self, audio_frame):
            return 0.9

    class FakeInputStream:
        def __init__(self, *args, **kwargs):
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert notification_sound_player.calls == 1


def test_wait_for_wake_word_skips_notification_sound_when_disabled(monkeypatch):
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
        wake_word_notification=False,
    )
    notification_sound_player = FakeNotificationSoundPlayer()
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )
    engine.notification_sound_player = notification_sound_player

    class FakeModel:
        def predict(self, audio_frame):
            return 0.9

    class FakeInputStream:
        def __init__(self, *args, **kwargs):
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert notification_sound_player.calls == 0


def test_wait_for_wake_word_continues_when_notification_sound_fails(
    monkeypatch,
    caplog,
):
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )
    notification_sound_player = FakeNotificationSoundPlayer(RuntimeError("no sound"))
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )
    engine.notification_sound_player = notification_sound_player

    class FakeModel:
        def predict(self, audio_frame):
            return 0.9

    class FakeInputStream:
        def __init__(self, *args, **kwargs):
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    with caplog.at_level(logging.WARNING, logger="baseLogger.adapter"):
        assert engine.wait_for_wake_word() is True

    assert notification_sound_player.calls == 1
    assert any(
        "Wake-word notification sound failed: no sound" in record.message
        for record in caplog.records
    )


def test_wait_for_wake_word_passes_device_to_input_stream(monkeypatch):
    device_name = "Conference Microphone"
    monkeypatch.setattr(
        AudioDeviceResolver,
        "resolve_input_device",
        lambda self, selector: 1,
    )
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=device_name,
    )
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )

    class FakeModel:
        last_audio_frame = None

        def __init__(self):
            self.calls = 0

        def predict(self, audio_frame):
            self.calls += 1
            FakeModel.last_audio_frame = audio_frame.copy()
            return 0.9

    class FakeInputStream:
        kwargs_seen = None

        def __init__(self, *args, **kwargs):
            FakeInputStream.kwargs_seen = kwargs
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(
        engine,
        "_format_device_info_log",
        lambda: {"index": 1, "name": device_name},
    )
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert FakeInputStream.kwargs_seen is not None
    assert FakeInputStream.kwargs_seen["device"] == 1
    assert FakeModel.last_audio_frame is not None
    assert FakeModel.last_audio_frame.dtype == np.int16
    assert FakeModel.last_audio_frame.ndim == 1


def test_wait_for_wake_word_uses_first_available_device_when_config_is_unset(
    monkeypatch,
):
    first_input_index = 3
    monkeypatch.setattr(
        AudioDeviceResolver,
        "resolve_input_device",
        lambda self, selector: first_input_index,
    )
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )

    class FakeModel:
        def predict(self, audio_frame):
            return 0.9

    class FakeInputStream:
        kwargs_seen = None

        def __init__(self, *args, **kwargs):
            FakeInputStream.kwargs_seen = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(
        engine,
        "_format_device_info_log",
        lambda: {"index": first_input_index, "name": "Laptop Array Microphone"},
    )
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert FakeInputStream.kwargs_seen["device"] == first_input_index


def test_wait_for_wake_word_logs_raw_dict_scores(monkeypatch, caplog):
    config = get_config(
        wake_word_phrase="hey keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )

    class FakeModel:
        def predict(self, audio_frame):
            return {"hey_keeper_v2": 0.9, "keeper": 0.1}

    class FakeInputStream:
        def __init__(self, *args, **kwargs):
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(engine, "_raise_if_instant_audio_read", lambda read_seconds: None)
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    with caplog.at_level(logging.DEBUG, logger="baseLogger.adapter"):
        assert engine.wait_for_wake_word() is True

    assert any("Wake-word raw scores:" in record.message for record in caplog.records)
    assert any(
        "Wake-word 'hey keeper' detected!" in record.message
        for record in caplog.records
    )


def test_wait_for_wake_word_raises_user_message_on_instant_audio_read(monkeypatch):
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device=None,
    )
    engine = OpenWakeWordEngine(
        config,
        threshold=0.5,
        sample_rate=16000,
        chunk_seconds=0.25,
    )
    monotonic_values = iter([9.0, 10.0, 10.05])

    class FakeModel:
        def predict(self, audio_frame):
            raise AssertionError("Instant audio reads should fail before scoring")

    class FakeInputStream:
        def __init__(self, *args, **kwargs):
            self.blocksize = kwargs["blocksize"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, frames):
            return np.zeros((frames, 1), dtype=np.float32), False

    monkeypatch.setattr(engine, "load_model", lambda: FakeModel())
    monkeypatch.setattr(engine, "_monotonic_seconds", lambda: next(monotonic_values))
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    with pytest.raises(AdapterError, match="may not be a functional microphone"):
        engine.wait_for_wake_word()
