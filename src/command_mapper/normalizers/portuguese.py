"""Portuguese speech normalizer."""

from __future__ import annotations

from src.command_mapper.normalizers.base import BaseCommandNormalizer
from src.command_mapper.normalizers.mappings import (
    CANONICAL_COMMANDS,
    PORTUGUESE_COMMAND_ALIASES,
    PORTUGUESE_DROP_TOKENS,
    PORTUGUESE_PHRASE_CORRECTIONS,
    PORTUGUESE_TOKEN_CORRECTIONS,
)


class PortugueseSpeechNormalizer(BaseCommandNormalizer):
    """Normalize Portuguese Vosk output into canonical English commands."""

    drop_tokens = PORTUGUESE_DROP_TOKENS
    phrase_corrections = PORTUGUESE_PHRASE_CORRECTIONS
    token_corrections = PORTUGUESE_TOKEN_CORRECTIONS
    command_aliases = PORTUGUESE_COMMAND_ALIASES
    fuzzy_candidates = tuple(dict.fromkeys((*CANONICAL_COMMANDS, *PORTUGUESE_COMMAND_ALIASES.keys())))
