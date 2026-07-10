import numpy as np
from pathlib import Path

from src.core.config import get_config
from src.speech.audio_device_resolver import AudioDeviceResolver
import src.speech.wakeword.engine as wakeword_engine
from src.speech.wakeword.engine import OpenWakeWordEngine
from src.speech.interfaces import CustumizableAudioInputMixin


class FakeAudioInput(CustumizableAudioInputMixin):
    def __init__(self, resolver=None):
        self.audio_device_resolver = resolver or AudioDeviceResolver()


def resolve_audio_input_device(device_name: str | None) -> int | None:
    return FakeAudioInput().resolve_input_device(device_name)


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


def test_resolve_openwakeword_feature_models_downloads_missing_assets(
    monkeypatch,
    tmp_path,
):
    package_root = tmp_path / "package"
    package_root.mkdir()
    cache_dir = tmp_path / "cache"
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
    monkeypatch.setattr(
        wakeword_engine,
        "OPENWAKEWORD_MODEL_DIR",
        package_root / "resources" / "models",
    )
    monkeypatch.setattr(wakeword_engine, "OPENWAKEWORD_CACHE_DIR", cache_dir)
    monkeypatch.setattr(wakeword_engine, "download_file", fake_download)

    engine = OpenWakeWordEngine(get_config(audio_input_device=None))
    melspec_path, embedding_path = engine._resolve_openwakeword_feature_models()

    assert Path(melspec_path) == cache_dir / "melspectrogram.onnx"
    assert Path(embedding_path) == cache_dir / "embedding_model.onnx"
    assert created_downloads == [
        ("https://example.invalid/melspectrogram.onnx", str(cache_dir)),
        ("https://example.invalid/embedding_model.onnx", str(cache_dir)),
    ]


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

        def predict(self, audio_frame):
            self.calls += 1
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
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert FakeInputStream.instances == 1
    assert FakeInputStream.read_calls == 2


def test_wait_for_wake_word_passes_device_to_input_stream(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_query_hostapis_safe",
        lambda self: [],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    config = get_config(
        wake_word_phrase="keeper",
        openwakeword_model_path="/tmp/custom_wakeword.onnx",
        audio_input_device="USB 2.0",
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

        def predict(self, audio_frame):
            self.calls += 1
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
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert FakeInputStream.kwargs_seen is not None
    assert FakeInputStream.kwargs_seen["device"] == 1


def test_resolve_audio_input_device_substring(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_query_hostapis_safe",
        lambda self: [],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device("USB 2.0") == 1


def test_wait_for_wake_word_uses_default_device_when_config_is_unset(
    monkeypatch,
):
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
    monkeypatch.setattr(wakeword_engine.sounddevice, "InputStream", FakeInputStream)

    assert engine.wait_for_wake_word() is True
    assert FakeInputStream.kwargs_seen["device"] is None
