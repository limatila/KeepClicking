"""Wake word detector implementations."""

from __future__ import annotations

import os

from openwakeword import Model
import sounddevice

from src.core.errors import AdapterError
from src.core.logging import ADAPTER_LOGGER

from src.speech.interfaces import WakeWordEngineInterface


class OpenWakeWordEngine(WakeWordEngineInterface):
	"""OpenWakeWord-based wake-word detector."""

	def __init__(
		self,
		wake_word_phrase: str,
		threshold: float = 0.5,
		sample_rate: int = 16000,
		chunk_seconds: float = 0.5,
	):
		self.wake_word_phrase = wake_word_phrase
		self.threshold = threshold
		self.sample_rate = sample_rate
		self.chunk_seconds = chunk_seconds
		self.model = None
		self.seconds_wainting = 0.0

	def load_model(self):
		if self.model is not None:
			return self.model

		if os.path.exists(self.wake_word_phrase):
			try:
				self.model = Model(wakeword_models=[self.wake_word_phrase])
				return self.model
			except Exception:
				pass

		try:
			self.model = Model()
		except Exception as err:
			raise AdapterError("OpenWakeWord model initialization failed") from err

		return self.model

	def score_frame(self, model, audio_frame):
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
		model = self.load_model()
		
		frames = int(self.sample_rate * self.chunk_seconds)
		if frames <= 0:
			raise AdapterError("Invalid wake-word frame size")

		while True:
			audio = sounddevice.rec(
				frames,
				samplerate=self.sample_rate,
				channels=1,
				dtype="float32",
			)
			sounddevice.wait()
			
			score = self.score_frame(model, audio.reshape(-1))
			ADAPTER_LOGGER.debug(f"[waiting {self.wake_word_phrase}] Listening for {self.seconds_wainting} seconds... Wake-word score: {score:.3f}")
			self.seconds_wainting += self.chunk_seconds

			if score >= self.threshold:
				self.seconds_wainting = 0.0
				ADAPTER_LOGGER.info(f"Wake-word '{self.wake_word_phrase}' detected!")
				return True
