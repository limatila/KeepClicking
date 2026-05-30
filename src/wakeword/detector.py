"""Wake word detector implementations."""

from __future__ import annotations

import os

from src.core.errors import AdapterError, OptionalDependencyError
from src.speech.interfaces import WakeWordEngine


class OpenWakeWordEngine:
	"""OpenWakeWord-based wake-word detector."""

	def __init__(
		self,
		wake_word_phrase: str,
		threshold: float = 0.5,
		sample_rate: int = 16000,
		chunk_seconds: float = 0.5,
	) -> None:
		self._wake_word_phrase = wake_word_phrase
		self._threshold = threshold
		self._sample_rate = sample_rate
		self._chunk_seconds = chunk_seconds
		self._model = None

	def _import_model(self):
		try:
			from openwakeword.model import Model
		except Exception as exc:
			try:
				from openwakeword import Model
			except Exception as inner_exc:
				raise OptionalDependencyError(
					"openwakeword is required for wake-word detection"
				) from inner_exc

		return Model

	def _import_sounddevice(self):
		try:
			import sounddevice
		except Exception as exc:
			raise OptionalDependencyError(
				"sounddevice is required for wake-word detection"
			) from exc

		return sounddevice

	def _load_model(self):
		if self._model is not None:
			return self._model

		Model = self._import_model()
		if os.path.exists(self._wake_word_phrase):
			try:
				self._model = Model(wakeword_models=[self._wake_word_phrase])
				return self._model
			except Exception:
				pass

		try:
			self._model = Model()
		except Exception as exc:
			raise AdapterError("OpenWakeWord model initialization failed") from exc

		return self._model

	def _score_frame(self, model, audio_frame):
		if hasattr(model, "predict"):
			scores = model.predict(audio_frame)
		elif hasattr(model, "infer"):
			scores = model.infer(audio_frame)
		else:
			raise AdapterError("OpenWakeWord model lacks a predict interface")

		if isinstance(scores, dict):
			return max(scores.values(), default=0.0)
		if isinstance(scores, (list, tuple)):
			return max(scores) if scores else 0.0
		try:
			return float(scores)
		except (TypeError, ValueError):
			return 0.0

	def wait_for_wake_word(self) -> bool:
		model = self._load_model()
		sounddevice = self._import_sounddevice()
		frames = int(self._sample_rate * self._chunk_seconds)
		if frames <= 0:
			raise AdapterError("Invalid wake-word frame size")

		while True:
			audio = sounddevice.rec(
				frames,
				samplerate=self._sample_rate,
				channels=1,
				dtype="float32",
			)
			sounddevice.wait()
			score = self._score_frame(model, audio.reshape(-1))
			if score >= self._threshold:
				return True
