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


def test_resolve_audio_input_device_unset_uses_first_available_input_device(monkeypatch):
    first_input_index = 4
    second_input_index = 9
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"index": 2, "name": "Playback Only Device", "max_input_channels": 0},
            {
                "index": first_input_index,
                "name": "Laptop Array Microphone",
                "max_input_channels": 1,
            },
            {
                "index": second_input_index,
                "name": "Desk Headset Microphone",
                "max_input_channels": 1,
            },
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device(None) == first_input_index
    assert resolve_audio_input_device("") == first_input_index


def test_resolve_audio_input_device_numeric_index(monkeypatch):
    device_index = 1
    device_name = "Conference Microphone"
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Device 0", "max_input_channels": 0},
            {"index": device_index, "name": device_name, "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device(str(device_index)) == device_index


def test_resolve_audio_input_device_substring_match(monkeypatch):
    device_index = 1
    device_name = "Conference Microphone"
    selector = device_name.split()[0]
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"index": device_index, "name": device_name, "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device(selector) == device_index
    assert resolve_audio_input_device(selector.casefold()) == device_index
    assert resolve_audio_input_device(selector.upper()) == device_index


def test_resolve_audio_input_device_normalized_match(monkeypatch):
    device_index = 1
    device_name = "Studio Deck Microphone"
    selector = device_name.replace(" ", "")
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"index": device_index, "name": device_name, "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    assert resolve_audio_input_device(selector) == device_index


def test_resolve_audio_input_device_matches_alsa_card_alias(monkeypatch):
    device_index = 1
    card_selector = "Headset"
    card_name = "Wireless Headset Adapter"
    selector = card_name.replace(" ", "")
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "front:CARD=Generic,DEV=0", "max_input_channels": 0},
            {
                "index": device_index,
                "name": f"front:CARD={card_selector},DEV=0",
                "max_input_channels": 2,
            },
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_alsa_cards",
        lambda self: {
            card_selector: {
                "short_name": card_selector,
                "card_name": card_name,
                "description": f"{card_name} at usb-0000:03:00.3-2, full speed",
            }
        },
    )

    assert resolve_audio_input_device(selector) == device_index


def test_resolve_audio_input_device_not_found(monkeypatch):
    device_name = "Conference Microphone"
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": "Built-in Microphone", "max_input_channels": 0},
            {"name": device_name, "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})

    with pytest.raises(AdapterError):
        resolve_audio_input_device("missing")


def test_windows_active_capture_filter_keeps_matching_devices(monkeypatch):
    active_device_name = "Conference Microphone"
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": active_device_name, "max_input_channels": 2},
            {"name": "Webcam Microphone", "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: frozenset({active_device_name}),
    )

    devices = AudioDeviceResolver().list_input_devices()

    assert [device["name"] for device in devices] == [active_device_name]


def test_windows_active_capture_filter_matches_partial_core_audio_name(monkeypatch):
    active_name_part = "Conference Input"
    device_name = f"Microphone ({active_name_part} Device)"
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": device_name, "max_input_channels": 2},
        ],
    )
    monkeypatch.setattr(AudioDeviceResolver, "_query_hostapis_safe", lambda self: [])
    monkeypatch.setattr(AudioDeviceResolver, "_load_alsa_cards", lambda self: {})
    monkeypatch.setattr(
        AudioDeviceResolver,
        "_load_windows_active_capture_device_names",
        lambda self: frozenset({active_name_part}),
    )

    devices = AudioDeviceResolver().list_input_devices()

    assert [device["name"] for device in devices] == [device_name]


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
    first_device_name = "Conference Microphone"
    second_device_name = "Webcam Microphone"
    monkeypatch.setattr(
        "src.speech.audio_device_resolver.sounddevice.query_devices",
        lambda: [
            {"name": first_device_name, "max_input_channels": 2},
            {"name": second_device_name, "max_input_channels": 2},
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
        first_device_name,
        second_device_name,
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
