"""Vosk speech adapter implementation."""

from __future__ import annotations

import json

import numpy as np
import sounddevice
from vosk import KaldiRecognizer, Model

from src.command_mapper.normalizers.mappings import (
    CANONICAL_COMMANDS,
    ENGLISH_COMMAND_ALIASES,
    PORTUGUESE_COMMAND_ALIASES,
)
from src.core.config import AppConfig
from src.core.errors import AdapterError
from src.core.logging import ADAPTER_LOGGER
from src.speech.interfaces import (
    CustumizableAudioInputMixin,
    SpeechAdapterInterface,
    WakeWordEngineInterface,
)


class VoskSpeechAdapter(CustumizableAudioInputMixin, SpeechAdapterInterface):
    """Vosk-based speech adapter with wake-word gating."""

    def __init__(self, config: AppConfig, wake_word_engine: WakeWordEngineInterface) -> None:
        self.config = config
        self.wake_word_engine = wake_word_engine
        self.sample_rate = 16000
        self.speech_model = None
        self.speech_recognizer = None
        self.device = self.resolve_input_device(config.audio_input_device)
        
        if not self.config.offline_model_path:
            raise AdapterError("offline_model_path must be configured for Vosk")

    def _build_command_grammar(self) -> str:
        command_phrases = list(
            dict.fromkeys(
                (
                    *CANONICAL_COMMANDS,
                    *ENGLISH_COMMAND_ALIASES.keys(),
                    *PORTUGUESE_COMMAND_ALIASES.keys(),
                    "[unk]",
                )
            )
        )
        return json.dumps(command_phrases)

    def _set_speech_models(self) -> None:
        if self.speech_recognizer is not None:
            return

        self.speech_model = Model(self.config.offline_model_path)
        self.speech_recognizer = KaldiRecognizer(
            self.speech_model, self.sample_rate, self._build_command_grammar()
        )

    def _record_audio(self) -> bytes:
        frames = int(self.sample_rate * self.config.wake_word_listen_seconds)
        if frames <= 0:
            return b""

        audio = sounddevice.rec(
            frames,
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            device=self.device,
        )
        sounddevice.wait()
        
        ADAPTER_LOGGER.info(f"Speech capture listening on device: {self.device}")
        
        stats = self.get_audio_levels(audio.astype(np.float32) / 32768.0)
        ADAPTER_LOGGER.debug(
            "Recorded audio amplitude: peak=%s, mean=%s",
            f"{stats['peak']:.4f}", f"{stats['mean']:.4f}"
        )
        return audio.tobytes()

    def next_text(self) -> str | None:
        try:
            if not self.wake_word_engine.wait_for_wake_word():
                return ""

            audio_bytes = self._record_audio()
            if not audio_bytes:
                return ""

            self._set_speech_models()
            recognizer = self.speech_recognizer
            if recognizer is None:
                return None

            if recognizer.AcceptWaveform(audio_bytes):
                result_json = recognizer.Result()
            else:
                result_json = recognizer.FinalResult()

            ADAPTER_LOGGER.debug("Raw Vosk recognition result: %s", result_json)

            try:
                recognized_text = json.loads(result_json).get("text", "")
                ADAPTER_LOGGER.debug("Recognized command text: %s", recognized_text)
                return recognized_text
            except json.JSONDecodeError:
                return ""
        except AdapterError:
            raise
        except Exception as err:
            raise AdapterError("Vosk adapter failure") from err

    def close(self) -> None:
        return None
