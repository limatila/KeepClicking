import numpy as np
import pytest

import src.speech.audio_device_resolver as audio_device_resolver
from src.core.errors import AdapterError
from src.speech.audio_device_resolver import AudioDeviceResolver
from src.speech.interfaces import CustumizableAudioInputMixin

_ORIGINAL_LOAD_WINDOWS_ACTIVE_CAPTURE_DEVICE_NAMES = (
    AudioDeviceResolver._load_windows_active_capture_device_names
)


@pytest.fixture(autouse=True)
def disable_windows_active_capture_filter(monkeypatch):
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: None,
    )


class FakeAudioInput(CustumizableAudioInputMixin):
    def __init__(self, resolver: AudioDeviceResolver | None = None):
        self.audio_device_resolver = resolver or AudioDeviceResolver()


def resolve_audio_input_device(device_name: str | None) -> int | None:
    return FakeAudioInput().resolve_input_device(device_name)


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
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device("1") == 1


def test_resolve_audio_input_device_substring_match(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device("USB 2.0") == 1
    assert resolve_audio_input_device("usb") == 1
    assert resolve_audio_input_device("USB") == 1


def test_resolve_audio_input_device_normalized_match(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device("USB2.0") == 1


def test_resolve_audio_input_device_matches_alsa_card_alias(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "front:CARD=Generic,DEV=0", "max_input_channels": 0},
            {"name": "front:CARD=Device,DEV=0", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_alsa_cards",
        lambda self: {
            "Device": {
                "short_name": "Device",
                "card_name": "USB2.0 Device",
                "description": "Generic USB2.0 Device at usb-0000:03:00.3-2, full speed",
            }
        },
    )

    assert resolve_audio_input_device("USB2.0") == 1


def test_resolve_audio_input_device_not_found(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    with pytest.raises(AdapterError):
        resolve_audio_input_device("missing")


def test_windows_active_capture_filter_keeps_matching_devices(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
            {"name": "Webcam Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: frozenset({"USB 2.0 Microphone"}),
    )

    devices = AudioDeviceResolver().list_input_devices()

    assert [device["name"] for device in devices] == ["USB 2.0 Microphone"]


def test_windows_active_capture_filter_matches_partial_core_audio_name(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Microphone (USB 2.0 Audio Device)", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: frozenset({"USB 2.0 Audio"}),
    )

    devices = AudioDeviceResolver().list_input_devices()

    assert [device["name"] for device in devices] == [
        "Microphone (USB 2.0 Audio Device)"
    ]


def test_windows_active_capture_filter_blocks_filtered_selector(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Active Microphone", "max_input_channels": 2},
            {"name": "Disconnected Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: frozenset({"Active Microphone"}),
    )

    with pytest.raises(AdapterError):
        resolve_audio_input_device("Disconnected")


def test_windows_active_capture_filter_falls_back_when_unavailable(monkeypatch):
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "USB 2.0 Microphone", "max_input_channels": 2},
            {"name": "Webcam Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: None,
    )

    devices = AudioDeviceResolver().list_input_devices()

    assert [device["name"] for device in devices] == [
        "USB 2.0 Microphone",
        "Webcam Microphone",
    ]


def test_load_windows_active_capture_device_names_skips_non_windows(monkeypatch):
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        _ORIGINAL_LOAD_WINDOWS_ACTIVE_CAPTURE_DEVICE_NAMES,
    )
    monkeypatch.setattr(audio_device_resolver.os, "name", "posix")

    assert AudioDeviceResolver()._load_windows_active_capture_device_names() is None


def test_load_windows_active_capture_device_names_returns_none_on_pycaw_error(
    monkeypatch,
):
    import builtins

    real_import = builtins.__import__

    def fail_pycaw_import(name, *args, **kwargs):
        if name.startswith("pycaw"):
            raise ImportError("pycaw unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        _ORIGINAL_LOAD_WINDOWS_ACTIVE_CAPTURE_DEVICE_NAMES,
    )
    monkeypatch.setattr(audio_device_resolver.os, "name", "nt")
    monkeypatch.setattr(builtins, "__import__", fail_pycaw_import)

    assert AudioDeviceResolver()._load_windows_active_capture_device_names() is None


def test_audio_levels():
    audio = np.array([[0.0], [0.5], [-0.5], [0.25]], dtype=np.float32)

    stats = FakeAudioInput().get_audio_levels(audio)

    assert stats["peak"] == pytest.approx(0.5)
    assert stats["mean"] == pytest.approx(0.3125)
