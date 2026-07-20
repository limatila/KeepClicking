"""Speech normalizer exports."""

from src.command_mapper.normalizers.english import EnglishSpeechNormalizer
from src.command_mapper.normalizers.portuguese import PortugueseSpeechNormalizer

__all__ = [
    "EnglishSpeechNormalizer",
    "PortugueseSpeechNormalizer",
]
