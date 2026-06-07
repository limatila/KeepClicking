"""Wake word detector implementations."""

from __future__ import annotations

import os

from openwakeword import Model
import sounddevice

from src.core.errors import AdapterError
from src.core.logging import ADAPTER_LOGGER
from src.core.config import AppConfig

from src.speech.interfaces import WakeWordEngineInterface


class OpenWakeWordEngine(WakeWordEngineInterface):
	"""OpenWakeWord-based wake-word detector."""

	def __init__(
		self,
		config: AppConfig,
		threshold: float = 0.5,
		sample_rate: int = 16000,
		chunk_seconds: float = 0.5,
	):
		self.wake_word_phrase = config.wake_word_phrase
		self.model_path = config.openwakeword_model_path
		self.threshold = threshold
		self.sample_rate = sample_rate
		self.chunk_seconds = chunk_seconds
		self.model: Model = None
		self.seconds_waiting = 0.0

	def load_model(self):
		try:
			if self.model is None:
				if not os.path.exists(self.model_path):
					raise FileNotFoundError("Wake-word model not found")

				self.model = Model(
						wakeword_models=[self.model_path], inference_framework="onnx"
					)

			return self.model

		except FileNotFoundError:
			raise

		except Exception as err:
			raise AdapterError("OpenWakeWord model initialization failed") from err


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

		with sounddevice.InputStream(
			samplerate=self.sample_rate,
			channels=1,
			dtype="float32",
			blocksize=frames,
		) as stream:
			while True:
				audio, _ = stream.read(frames)
				score = self.score_frame(model, audio.reshape(-1))

				ADAPTER_LOGGER.debug(
					f"[waiting {self.wake_word_phrase}] Listening for {self.seconds_waiting} seconds... Wake-word score: {score:.3f}"
				)
				self.seconds_waiting += self.chunk_seconds

				if score >= self.threshold:
					self.seconds_waiting = 0.0
					ADAPTER_LOGGER.info(f"Wake-word '{self.wake_word_phrase}' detected!")
					return True
