import json
import numpy as np

from src.command_mapper.normalizers.mappings import (
    CANONICAL_COMMANDS,
    ENGLISH_COMMAND_ALIASES,
    PORTUGUESE_COMMAND_ALIASES,
)
from src.core.config import get_config
from src.speech.audio_device_resolver import AudioDeviceResolver
import src.speech.offline_adapters.offline_vosk_adapter as vosk_adapter
from src.speech.offline_adapters.offline_vosk_adapter import VoskSpeechAdapter


class DummyWakeWordEngine:
    def wait_for_wake_word(self):
        return True


def test_set_speech_models_uses_command_grammar(monkeypatch):
    monkeypatch.setattr(
        AudioDeviceResolver,
        "resolve_input_device",
        lambda self, selector: 1,
    )
    config = get_config(audio_input_device=None, offline_model_path="/tmp/model")
    adapter = VoskSpeechAdapter(config, DummyWakeWordEngine())
    recognizer_args = {}

    class FakeModel:
        def __init__(self, model_path):
            recognizer_args["model_path"] = model_path

    class FakeRecognizer:
        def __init__(self, model, sample_rate, grammar):
            recognizer_args["sample_rate"] = sample_rate
            recognizer_args["grammar"] = grammar

    monkeypatch.setattr(vosk_adapter, "Model", FakeModel)
    monkeypatch.setattr(vosk_adapter, "KaldiRecognizer", FakeRecognizer)

    adapter._set_speech_models()
    parsed_grammar = json.loads(recognizer_args["grammar"])
    expected_grammar = list(
        dict.fromkeys(
            (
                *CANONICAL_COMMANDS,
                *ENGLISH_COMMAND_ALIASES.keys(),
                *PORTUGUESE_COMMAND_ALIASES.keys(),
                "[unk]",
            )
        )
    )

    assert recognizer_args["model_path"] == "/tmp/model"
    assert recognizer_args["sample_rate"] == 16000
    assert parsed_grammar == expected_grammar
    assert "double click" in parsed_grammar
    assert "two click" in parsed_grammar
    assert "mouse up" in parsed_grammar
    assert "[unk]" in parsed_grammar


def test_record_audio_passes_device_to_sounddevice_rec(monkeypatch):
    device_name = "Conference Microphone"
    monkeypatch.setattr(
        AudioDeviceResolver,
        "resolve_input_device",
        lambda self, selector: 1,
    )

    config = get_config(audio_input_device=device_name, offline_model_path="/tmp/model")
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


def test_record_audio_uses_first_available_device_when_config_is_unset(monkeypatch):
    first_input_index = 3
    monkeypatch.setattr(
        AudioDeviceResolver,
        "resolve_input_device",
        lambda self, selector: first_input_index,
    )
    config = get_config(audio_input_device=None, offline_model_path="/tmp/model")
    adapter = VoskSpeechAdapter(config, DummyWakeWordEngine())

    rec_kwargs = {}

    def fake_rec(*args, **kwargs):
        rec_kwargs.update(kwargs)
        return np.zeros((16000, 1), dtype=np.int16)

    monkeypatch.setattr(vosk_adapter.sounddevice, "rec", fake_rec)
    monkeypatch.setattr(vosk_adapter.sounddevice, "wait", lambda: None)

    adapter._record_audio()

    assert rec_kwargs["device"] == first_input_index
