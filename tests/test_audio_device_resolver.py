import numpy as np
import pytest

from src.core.errors import AdapterError
from src.speech.interfaces import get_amplitude_stats
from src.speech.interfaces import resolve_audio_input_device


def test_resolve_audio_input_device_none_returns_none():
    assert resolve_audio_input_device(None) is None
    assert resolve_audio_input_device("") is None


def test_resolve_audio_input_device_numeric_index(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Device 0", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )

    assert resolve_audio_input_device("1") == 1


def test_resolve_audio_input_device_substring_match(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )

    assert resolve_audio_input_device("USB 2.0") == 1
    assert resolve_audio_input_device("usb") == 1


def test_resolve_audio_input_device_not_found(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )

    with pytest.raises(AdapterError):
        resolve_audio_input_device("missing")


def test_get_amplitude_stats():
    audio = np.array([[0.0], [0.5], [-0.5], [0.25]], dtype=np.float32)

    stats = get_amplitude_stats(audio)

    assert stats["peak"] == pytest.approx(0.5)
    assert stats["mean"] == pytest.approx(0.3125)