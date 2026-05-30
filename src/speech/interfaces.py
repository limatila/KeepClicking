"""Speech adapter interfaces."""

from __future__ import annotations

from typing import Protocol


class SpeechAdapter(Protocol):
	"""Base interface for speech adapters."""

	def next_text(self) -> str | None:
		"""Return the next recognized phrase, or None on end-of-stream."""

	def close(self) -> None:
		"""Release adapter resources."""


class WakeWordEngine(Protocol):
	"""Base interface for wake-word engines."""

	def wait_for_wake_word(self) -> bool:
		"""Block until the wake word is detected and return True."""
