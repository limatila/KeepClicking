"""Vosk speech adapter implementation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import sounddevice
from vosk import KaldiRecognizer, Model, SetLogLevel as set_vosk_log_level

from src.command_mapper.normalizers.mappings import (
    resolve_recognition_phrases,
)
from src.core.config import AppConfig
from src.core.errors import AdapterError
from src.core.logging import ADAPTER_LOGGER

from src.speech.interfaces import (
    CustumizableAudioInputMixin,
    SpeechAdapterInterface,
    WakeWordEngineInterface,
)
from src.utils.notifications import NotificationSoundPlayer, build_notification_sound_player


class VoskSpeechAdapter(CustumizableAudioInputMixin, SpeechAdapterInterface):
    """Vosk-based speech adapter with wake-word gating."""

    def __init__(self, config: AppConfig, wake_word_engine: WakeWordEngineInterface) -> None:
        self.config = config
        self.wake_word_engine = wake_word_engine
        self.sample_rate = 16000
        self.speech_model = None
        self.speech_recognizer = None
        self.device = self.resolve_input_device(config.audio_input_device)
        self.notification_sound_player = build_notification_sound_player()
        
        if not self.config.offline_model_path:
            raise AdapterError("offline_model_path must be configured for Vosk")

    @property
    def command_grammar(self) -> str:
        command_phrases = [
            *resolve_recognition_phrases(self.config.speech_language),
            "[unk]",
        ]
        return json.dumps(command_phrases)

    def _set_speech_models(self) -> None:
        if self.speech_recognizer is not None:
            return

        model_path = Path(self.config.offline_model_path)
       
        if not model_path.exists() or not model_path.is_dir():
            raise AdapterError(
                f"Vosk model path '{self.config.offline_model_path}' for speech_language '{self.config.speech_language.value}' was not found. "
                "This packaged EXE only contains its matching bundled language model. If you changed offline_model_path in a local .env file, "
                "point it to an existing en_us Vosk model directory as in project structure."
            )

        set_vosk_log_level(-1)
        ADAPTER_LOGGER.info("Loading Vosk model from '%s'.", model_path)
        ADAPTER_LOGGER.info("Loaded Vosk grammar: %s", self.command_grammar)

        self.speech_model = Model(self.config.offline_model_path)
        self.speech_recognizer = KaldiRecognizer(
            self.speech_model, self.sample_rate, self.command_grammar
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

                if not recognized_text:
                    ADAPTER_LOGGER.info("speech_error: no_valid_text_recognized")
                    self.notification_sound_player.play_speech_error()

                return recognized_text

            except json.JSONDecodeError:
                ADAPTER_LOGGER.warning("speech_error: invalid_vosk_result_json")
                self.notification_sound_player.play_speech_error()

                return ""

        except AdapterError:
            raise

        except Exception as err:
            raise AdapterError("Vosk adapter failure") from err

    def close(self) -> None:
        return None
