"""Compatibility exports for speech normalizers."""

from __future__ import annotations

from src.command_mapper.interfaces import CommandNormalizer
from src.command_mapper.normalizers.english import EnglishSpeechNormalizer
from src.command_mapper.normalizers.portuguese import PortugueseSpeechNormalizer
from src.core.choices import SpeechLanguage


def resolve_command_normalizer(language: SpeechLanguage) -> CommandNormalizer:
    """Dispatch the configured language to its normalizer strategy."""

    match language:
        case SpeechLanguage.PT_BR:
            return PortugueseSpeechNormalizer()
        case SpeechLanguage.EN_US:
            return EnglishSpeechNormalizer()


def normalize_text(raw_text: str) -> str:
    """Normalize text using the default configured command language."""

    return resolve_command_normalizer(SpeechLanguage.EN_US).normalize(raw_text)
