"""Wake word detector implementations."""

from __future__ import annotations

import os
from pathlib import Path

import openwakeword
from openwakeword import Model
from openwakeword.utils import download_file
import sounddevice

from src.core.errors import AdapterError
from src.core.logging import ADAPTER_LOGGER
from src.core.config import AppConfig

from src.speech.interfaces import WakeWordEngineInterface, CustumizableAudioInputMixin

OPENWAKEWORD_MODEL_DIR = Path(openwakeword.__file__).resolve().parent / "resources" / "models"
OPENWAKEWORD_CACHE_DIR = Path(__file__).resolve().parents[3] / ".cache" / "openwakeword"


class OpenWakeWordEngine(CustumizableAudioInputMixin, WakeWordEngineInterface):
	"""OpenWakeWord-based wake-word detector."""

	def __init__(
		self,
		config: AppConfig,
		threshold: float = 0.5,
		sample_rate: int = 16000,
		chunk_seconds: float = 0.5,
	):
		self.wake_word_phrase = config.wake_word_phrase
		self.model_path = str(config.openwakeword_model_path)
		self.threshold = threshold
		self.sample_rate = sample_rate
		self.chunk_seconds = chunk_seconds
		self.model: Model = None
		self.seconds_waiting = 0.0
		self.device_index = self.resolve_input_device(config.audio_input_device)

	def _resolve_openwakeword_feature_models(self) -> tuple[str, str]:
		packaged_melspec_path = OPENWAKEWORD_MODEL_DIR / "melspectrogram.onnx"
		packaged_embedding_path = OPENWAKEWORD_MODEL_DIR / "embedding_model.onnx"
		if packaged_melspec_path.exists() and packaged_embedding_path.exists():
			return str(packaged_melspec_path), str(packaged_embedding_path)

		cache_melspec_path = OPENWAKEWORD_CACHE_DIR / "melspectrogram.onnx"
		cache_embedding_path = OPENWAKEWORD_CACHE_DIR / "embedding_model.onnx"
		missing_assets = {
			"melspectrogram": cache_melspec_path,
			"embedding": cache_embedding_path,
		}
		if not all(path.exists() for path in missing_assets.values()):
			self._download_openwakeword_feature_models(missing_assets)

		if not cache_melspec_path.exists() or not cache_embedding_path.exists():
			raise AdapterError(
				"OpenWakeWord support assets are missing. Expected "
				f"'{cache_melspec_path}' and '{cache_embedding_path}'."
			)

		return str(cache_melspec_path), str(cache_embedding_path)

	def _download_openwakeword_feature_models(self, target_paths: dict[str, Path]) -> None:
		OPENWAKEWORD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
		try:
			for asset_name, target_path in target_paths.items():
				if target_path.exists():
					continue

				download_url = openwakeword.FEATURE_MODELS[asset_name]["download_url"].replace(".tflite", ".onnx")
				ADAPTER_LOGGER.warning(
					"OpenWakeWord asset '%s' was missing; downloading it to '%s'.",
					target_path.name,
					target_path,
				)
				download_file(download_url, str(OPENWAKEWORD_CACHE_DIR))
		except Exception as err:
			raise AdapterError(
				"OpenWakeWord support assets are missing and could not be downloaded automatically. "
				f"Checked '{OPENWAKEWORD_MODEL_DIR}' and '{OPENWAKEWORD_CACHE_DIR}'."
			) from err

	def load_model(self):
		try:
			if self.model is None:
				if not os.path.exists(self.model_path):
					raise FileNotFoundError("Wake-word model not found")

				melspec_model_path, embedding_model_path = self._resolve_openwakeword_feature_models()
				self.model = Model(
					wakeword_models=[self.model_path],
					inference_framework="onnx",
					melspec_model_path=melspec_model_path,
					embedding_model_path=embedding_model_path,
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
			device=self.device_index,
		) as stream:
			ADAPTER_LOGGER.info(f"Wake-word engine listening on device: {self.device_index}")
			while True:
				audio, _ = stream.read(frames)
				score = self.score_frame(model, audio.reshape(-1))
				stats = self.get_audio_levels(audio)

				ADAPTER_LOGGER.debug(
					f"[waiting {self.wake_word_phrase}] Listening for {self.seconds_waiting} seconds... Wake-word score: {score:.3f} | "
					f"Amplitude peak={stats['peak']:.4f}, mean={stats['mean']:.4f}"
				)
				self.seconds_waiting += self.chunk_seconds

				if score >= self.threshold:
					self.seconds_waiting = 0.0
					ADAPTER_LOGGER.info(f"Wake-word '{self.wake_word_phrase}' detected!")
					return True
