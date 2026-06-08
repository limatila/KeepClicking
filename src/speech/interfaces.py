"""Speech adapter interfaces."""

from __future__ import annotations

from typing import Protocol

import numpy as np

import sounddevice

from src.core.errors import AdapterError


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

	def resolve_audio_input_device(device_selector: str | None) -> int | None:
		"""Resolve a configured selector to a sounddevice input device index."""
		if device_selector is None:
			return None

		selector = device_selector.strip()
		if selector == "":
			return None

		devices = sounddevice.query_devices()

		try:
			device_index = int(selector)
		except ValueError:
			device_index = None

		if device_index is not None:
			if 0 <= device_index < len(devices):
				device_info = devices[device_index]
				if device_info.get("max_input_channels", 0) > 0:
					return device_index
			raise AdapterError(f"Audio input device index '{selector}' is not a valid input device")

		selector_lower = selector.lower()
		for index, device_info in enumerate(devices):
			if device_info.get("max_input_channels", 0) <= 0:
				continue

			device_name = str(device_info.get("name", ""))
			if selector_lower in device_name.lower():
				return index

		raise AdapterError(f"Audio input device '{selector}' not found")


	def get_amplitude_stats(audio: np.ndarray) -> dict[str, float]:
		"""Return simple peak and mean amplitude statistics for captured audio."""
		abs_audio = np.abs(audio)
		return {
			"peak": float(np.max(abs_audio)) if abs_audio.size else 0.0,
			"mean": float(np.mean(abs_audio)) if abs_audio.size else 0.0,
		}
