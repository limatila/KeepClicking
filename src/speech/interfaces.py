"""Speech adapter interfaces."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from src.speech.audio_device_resolver import AudioDeviceResolver


class SpeechAdapterInterface(Protocol):
    """Base interface for speech adapters."""

    def next_text(self) -> str | None:
        """Return the next recognized phrase, or None on end-of-stream."""

    def close(self) -> None:
        """Release adapter resources."""


class WakeWordEngineInterface(Protocol):
    """Base interface for wake-word engines."""

    def wait_for_wake_word(self) -> bool:
        """Block until the wake word is detected and return True."""


class CustumizableAudioInputMixin:
    """Mixin to allow custom audio input device resolution for speech adapters."""

    resolver = AudioDeviceResolver()

    def resolve_input_device(self, device_name: str | None) -> int | None:
        """Resolve a configured selector to a sounddevice input device index."""
        return self.resolver.resolve_input_device(device_name)

    def get_audio_levels(self, audio: np.ndarray) -> dict[str, float]:
        """Return simple peak and mean amplitude statistics for captured audio."""
        abs_audio = np.abs(audio)
        return {
            "peak": float(np.max(abs_audio)) if abs_audio.size else 0.0,
            "mean": float(np.mean(abs_audio)) if abs_audio.size else 0.0,
        }
