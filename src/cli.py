"""Dev-ambient CLI runner for testing and development """

from src.core.logging import CORE_LOGGER
from src.core.config import get_config

from src.service.application_runner import MouseApplicationRunner

from src.speech.wakeword.engine import OpenWakeWordEngine
from src.speech.offline_vosk_adapter import VoskSpeechAdapter
from src.command_mapper.normalizer import normalize_text
from src.command_mapper.parser import MouseCommandParser
from src.command_mapper.validator import MouseCommandValidator
from src.service.hardware_controller import PyAutoGuiMouseController

APP_CONFIG = get_config(debug_mode=True)


def main():
    CORE_LOGGER.info("![DEV] Starting KeepClicking CLI runner...\n")
    
    runner = MouseApplicationRunner(
        adapter=VoskSpeechAdapter(
            APP_CONFIG, OpenWakeWordEngine(APP_CONFIG)
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
