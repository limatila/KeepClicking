"""English speech normalizer."""

from __future__ import annotations

from src.command_mapper.normalizers.base import BaseCommandNormalizer
from src.command_mapper.normalizers.mappings import (
    CANONICAL_COMMANDS,
    ENGLISH_COMMAND_ALIASES,
    ENGLISH_DROP_TOKENS,
    ENGLISH_PHRASE_CORRECTIONS,
    ENGLISH_TOKEN_CORRECTIONS,
)


class EnglishSpeechNormalizer(BaseCommandNormalizer):
    """Normalize English Vosk output into canonical command phrases."""

    drop_tokens = ENGLISH_DROP_TOKENS
    phrase_corrections = ENGLISH_PHRASE_CORRECTIONS
    token_corrections = ENGLISH_TOKEN_CORRECTIONS
    command_aliases = ENGLISH_COMMAND_ALIASES
    fuzzy_candidates = tuple(dict.fromkeys((*CANONICAL_COMMANDS, *ENGLISH_COMMAND_ALIASES.keys())))
