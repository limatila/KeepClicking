import numpy as np

from src.core.config import get_config
from src.speech.audio_device_resolver import AudioDeviceResolver
import src.speech.offline_adapters.offline_vosk_adapter as vosk_adapter
from src.speech.offline_adapters.offline_vosk_adapter import VoskSpeechAdapter


class DummyWakeWordEngine:
    def wait_for_wake_word(self):
        return True


def test_record_audio_passes_device_to_sounddevice_rec(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    config = get_config(audio_input_device="USB 2.0", offline_model_path="/tmp/model")
    adapter = VoskSpeechAdapter(config, DummyWakeWordEngine())

    rec_kwargs = {}

    def fake_rec(*args, **kwargs):
        rec_kwargs.update(kwargs)
        return np.zeros((16000, 1), dtype=np.int16)

    monkeypatch.setattr(vosk_adapter.sounddevice, "rec", fake_rec)
    monkeypatch.setattr(vosk_adapter.sounddevice, "wait", lambda: None)

    audio = adapter._record_audio()

    assert audio
    assert rec_kwargs["device"] == 1


def test_record_audio_uses_default_device_when_config_is_unset(monkeypatch):
    config = get_config(audio_input_device=None, offline_model_path="/tmp/model")
    adapter = VoskSpeechAdapter(config, DummyWakeWordEngine())

    rec_kwargs = {}

    def fake_rec(*args, **kwargs):
        rec_kwargs.update(kwargs)
        return np.zeros((16000, 1), dtype=np.int16)

    monkeypatch.setattr(vosk_adapter.sounddevice, "rec", fake_rec)
    monkeypatch.setattr(vosk_adapter.sounddevice, "wait", lambda: None)

    adapter._record_audio()

    assert rec_kwargs["device"] is None
