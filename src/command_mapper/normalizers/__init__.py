"""Speech normalizer exports."""

from src.command_mapper.normalizers.english import EnglishSpeechNormalizer
from src.command_mapper.normalizers.portuguese import PortugueseSpeechNormalizer
from src.command_mapper.normalizer_dispatchers import resolve_command_normalizer

__all__ = [
    "EnglishSpeechNormalizer",
    "PortugueseSpeechNormalizer",
    "resolve_command_normalizer",
]
