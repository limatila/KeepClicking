"""Dev-only keyboard speech adapter."""

from __future__ import annotations

from src.speech.interfaces import SpeechAdapterInterface


class KeyboardSpeechAdapter:
	"""Speech adapter that reads commands from terminal input."""

	def __init__(self, prompt: str) -> None:
		self._prompt = prompt

	def next_text(self) -> str | None:
		try:
			return input(self._prompt)
		except EOFError:
			return None

	def close(self) -> None:
		return None
