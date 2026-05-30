"""Vosk speech adapter implementation."""

from __future__ import annotations

import json

from src.core.config import AppConfig
from src.core.errors import AdapterError, OptionalDependencyError
from src.speech.interfaces import SpeechAdapter, WakeWordEngine


class VoskSpeechAdapter:
	"""Vosk-based speech adapter with wake-word gating."""

	def __init__(self, config: AppConfig, wake_word_engine: WakeWordEngine) -> None:
		self._config = config
		self._wake_word_engine = wake_word_engine
		self._sample_rate = 16000
		self._model = None
		self._recognizer = None

	def _import_sounddevice(self):
		try:
			import sounddevice
		except Exception as exc:
			raise OptionalDependencyError(
				"sounddevice is required for offline speech recognition"
			) from exc

		return sounddevice

	def _import_vosk(self):
		try:
			from vosk import KaldiRecognizer, Model
		except Exception as exc:
			raise OptionalDependencyError(
				"vosk is required for offline speech recognition"
			) from exc

		return Model, KaldiRecognizer

	def _ensure_recognizer(self) -> None:
		if self._recognizer is not None:
			return

		if not self._config.offline_model_path:
			raise AdapterError("offline_model_path must be configured for Vosk")

		Model, KaldiRecognizer = self._import_vosk()
		self._model = Model(self._config.offline_model_path)
		self._recognizer = KaldiRecognizer(self._model, self._sample_rate)

	def _record_audio(self) -> bytes:
		sounddevice = self._import_sounddevice()
		frames = int(self._sample_rate * self._config.wake_word_listen_seconds)
		if frames <= 0:
			return b""

		audio = sounddevice.rec(
			frames,
			samplerate=self._sample_rate,
			channels=1,
			dtype="int16",
		)
		sounddevice.wait()
		return audio.tobytes()

	def next_text(self) -> str | None:
		try:
			if not self._wake_word_engine.wait_for_wake_word():
				return ""

			audio_bytes = self._record_audio()
			if not audio_bytes:
				return ""

			self._ensure_recognizer()
			recognizer = self._recognizer
			if recognizer is None:
				return None

			if recognizer.AcceptWaveform(audio_bytes):
				result_json = recognizer.Result()
			else:
				result_json = recognizer.FinalResult()

			try:
				return json.loads(result_json).get("text", "")
			except json.JSONDecodeError:
				return ""
		except OptionalDependencyError:
			raise
		except AdapterError:
			raise
		except Exception as exc:
			raise AdapterError("Vosk adapter failure") from exc

	def close(self) -> None:
		return None
