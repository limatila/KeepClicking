"""Wake word detector implementations."""

from __future__ import annotations

import os
import time
from pathlib import Path

import numpy as np
import openwakeword
import sounddevice
from openwakeword import Model
from openwakeword.utils import download_file

from src.core.config import AppConfig, OPENWAKEWORD_LIB_CACHE_DIR, OPENWAKEWORD_LIB_MODEL_DIR
from src.core.errors import AdapterError
from src.core.logging import ADAPTER_LOGGER
from src.speech.interfaces import (
    CustumizableAudioInputMixin,
    WakeWordEngineInterface,
)


class OpenWakeWordEngine(CustumizableAudioInputMixin, WakeWordEngineInterface):
    """OpenWakeWord-based wake-word detector."""

    def __init__(self, config: AppConfig, threshold: float = 0.35, sample_rate: int = 16000, chunk_seconds: float = 0.5):
        self.wake_word_phrase = config.wake_word_phrase
        self.model_path = str(config.openwakeword_model_path)
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_seconds = chunk_seconds
        self.model: Model = None
        self.seconds_waiting = 0.0
        self.device_index = self.resolve_input_device(config.audio_input_device)

    def _resolve_openwakeword_feature_models(self) -> tuple[str, str]:
        packaged_melspec_path = OPENWAKEWORD_LIB_MODEL_DIR / "melspectrogram.onnx"
        packaged_embedding_path = OPENWAKEWORD_LIB_MODEL_DIR / "embedding_model.onnx"
        if packaged_melspec_path.exists() and packaged_embedding_path.exists():
            return str(packaged_melspec_path), str(packaged_embedding_path)

        cache_melspec_path = OPENWAKEWORD_LIB_CACHE_DIR / "melspectrogram.onnx"
        cache_embedding_path = OPENWAKEWORD_LIB_CACHE_DIR / "embedding_model.onnx"
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
        OPENWAKEWORD_LIB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            for asset_name, target_path in target_paths.items():
                if target_path.exists():
                    continue

                download_url = openwakeword.FEATURE_MODELS[asset_name][
                    "download_url"
                ].replace(".tflite", ".onnx")
                ADAPTER_LOGGER.warning(
                    "OpenWakeWord asset '%s' was missing; downloading it to '%s'.",
                    target_path.name,
                    target_path,
                )
                download_file(download_url, str(OPENWAKEWORD_LIB_CACHE_DIR))
        except Exception as err:
            raise AdapterError(
                "OpenWakeWord support assets are missing and could not be "
                "downloaded automatically. "
                f"Checked '{OPENWAKEWORD_LIB_MODEL_DIR}' and "
                f"'{OPENWAKEWORD_LIB_CACHE_DIR}'."
            ) from err

    def load_model(self) -> Model:
        try:
            if self.model is None:
                if not os.path.exists(self.model_path):
                    raise FileNotFoundError("Wake-word model not found")

                melspec_model_path, embedding_model_path = (
                    self._resolve_openwakeword_feature_models()
                )
                ADAPTER_LOGGER.info(
                    "Loading wake-word model from '%s' with support assets "
                    "'%s' and '%s'.",
                    self.model_path,
                    melspec_model_path,
                    embedding_model_path,
                )
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
            raise AdapterError(
                "OpenWakeWord model initialization failed"
            ) from err

    def _prepare_model_audio_frame(self, audio: np.ndarray) -> np.ndarray:
        audio_frame = np.asarray(audio, dtype=np.float32).reshape(-1)
        audio_frame = np.clip(audio_frame, -1.0, 1.0)
        return (audio_frame * 32767.0).astype(np.int16)

    def _predict_scores(self, model: Model, audio_frame: np.ndarray):
        if hasattr(model, "predict"):
            return model.predict(audio_frame)
        if hasattr(model, "infer"):
            return model.infer(audio_frame)
        raise AdapterError("OpenWakeWord model lacks a predict interface")

    def _extract_score(self, scores) -> float:
        if isinstance(scores, dict):
            return max(scores.values(), default=0.0)
        if isinstance(scores, (list, tuple, np.ndarray)):
            if len(scores) == 0:
                return 0.0
            try:
                return float(np.max(scores))
            except (TypeError, ValueError):
                return 0.0

        try:
            return float(scores)
        except (TypeError, ValueError):
            return 0.0

    def _format_score_details(self, scores) -> str:
        if isinstance(scores, dict):
            formatted_scores = []
            for label, value in scores.items():
                try:
                    formatted_scores.append(f"{label}={float(value):.3f}")
                except (TypeError, ValueError):
                    formatted_scores.append(f"{label}={value!r}")
            return ", ".join(formatted_scores)

        return repr(scores)

    def score_frame(self, model: Model, audio_frame: np.ndarray) -> float:
        scores = self._predict_scores(model, audio_frame)
        return self._extract_score(scores)

    def _monotonic_seconds(self) -> float:
        return time.monotonic()

    def _raise_if_instant_audio_read(self, read_seconds: float) -> None:
        if read_seconds > 0.1:
            return

        raise AdapterError(
            "Audio device read returned too quickly "
            f"({read_seconds:.3f}s). The selected audio input "
            f"({self.device_index}) may not be a functional microphone. "
            "Choose a different audio_input_device."
        )

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
            ADAPTER_LOGGER.info(
                "Wake-word engine listening on device: %s | model=%s | "
                "threshold=%.3f",
                self.audio_device_resolver.get_device_info_for_index(self.device_index),
                self.model_path,
                self.threshold,
            )
            
            waiting_started_at = self._monotonic_seconds()
            self.seconds_waiting = 0.0
            while True:
                read_started_at = self._monotonic_seconds()
                audio, _ = stream.read(frames)
                self._raise_if_instant_audio_read(
                    self._monotonic_seconds() - read_started_at
                )

                model_audio_frame = self._prepare_model_audio_frame(audio)
                scores = self._predict_scores(model, model_audio_frame)
                score = self._extract_score(scores)
                mic_stats = self.get_audio_levels(audio)
                model_frame_stats = self.get_audio_levels(
                    model_audio_frame.astype(np.float32) / 32767.0
                )
                ADAPTER_LOGGER.debug(
                    "[waiting %s] Listening for %.2f seconds... Wake-word "
                    "score: %.3f | Mic amplitude peak=%.4f, mean=%.4f | "
                    "Model frame dtype=%s, peak=%.4f, mean=%.4f",
                    self.wake_word_phrase,
                    self.seconds_waiting,
                    score,
                    mic_stats["peak"],
                    mic_stats["mean"],
                    model_audio_frame.dtype,
                    model_frame_stats["peak"],
                    model_frame_stats["mean"],
                )
                if isinstance(scores, dict):
                    ADAPTER_LOGGER.debug(
                        f"Wake-word raw scores: {self._format_score_details(scores)}",
                    )
                self.seconds_waiting = self._monotonic_seconds() - waiting_started_at

                if score >= self.threshold:
                    self.seconds_waiting = 0.0
                    ADAPTER_LOGGER.info(f"Wake-word '{self.wake_word_phrase}' detected!")
                    
                    return True
