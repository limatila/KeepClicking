import numpy as np

from src.core.config import get_config
import src.speech.wakeword.engine as wakeword_engine
from src.speech.wakeword.engine import OpenWakeWordEngine


def test_load_model_uses_configured_model_path(monkeypatch):
    created_models = []
    config = get_config(openwakeword_model_path="/tmp/custom_wakeword.onnx")

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
    model = engine.load_model()

    assert isinstance(model, FakeModel)
    assert created_models == [
        ((), {"wakeword_models": [config.openwakeword_model_path], "inference_framework": "onnx"})
    ]


def test_wait_for_wake_word_reuses_one_input_stream(monkeypatch):
    config = get_config(wake_word_phrase="keeper", openwakeword_model_path="/tmp/custom_wakeword.onnx")
    engine = OpenWakeWordEngine(config, threshold=0.5, sample_rate=16000, chunk_seconds=0.25)

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