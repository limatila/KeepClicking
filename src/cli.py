"""Dev-ambient CLI runner for testing and development """

from src.core.logging import CORE_LOGGER
from src.core.config import get_config

from src.service.runner import MouseApplicationRunner

from src.wakeword.detector import OpenWakeWordEngine
from src.speech.offline_vosk_adapter import VoskSpeechAdapter
from src.commands.normalizer import normalize_text
from src.commands.parser import MouseCommandParser
from src.commands.validator import MouseCommandValidator
from src.service.hardware_controller import PyAutoGuiMouseController

APP_CONFIG = get_config(debug_mode=True)


def main():
    CORE_LOGGER.info("![DEV] Starting KeepClicking CLI runner...\n")
    
    runner = MouseApplicationRunner(
        adapter=VoskSpeechAdapter(
            APP_CONFIG, OpenWakeWordEngine(APP_CONFIG.wake_word_phrase)
        ),
        normalizer=normalize_text,
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=PyAutoGuiMouseController(),
        config=APP_CONFIG,
    )
    runner.run()


if __name__ == "__main__":
    main()
