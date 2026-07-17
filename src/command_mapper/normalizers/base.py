"""Base implementation for speech normalizers."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence

from rapidfuzz import fuzz, process

from src.core.errors import NormalizationError


class BaseCommandNormalizer:
    """Reusable staged normalizer for speech transcription cleanup."""

    drop_tokens: frozenset[str] = frozenset()
    phrase_corrections: Mapping[str, str] = {}
    token_corrections: Mapping[str, str] = {}
    command_aliases: Mapping[str, str] = {}
    fuzzy_candidates: Sequence[str] = ()
    fuzzy_score_cutoff: int = 93
    max_fuzzy_length: int = 32
    max_fuzzy_tokens: int = 5

    def normalize(self, text: str) -> str:
        try:
            sanitized = self.sanitize_text(text)
            if sanitized == "":
                return ""

            corrected = self.correct_incongruences(sanitized)
            canonical = self.map_to_canonical_command(corrected)
            if canonical is not None:
                return canonical

            fuzzy_match = self.resolve_fuzzy_candidate(corrected)
            return fuzzy_match or corrected

        except NormalizationError:
            raise
        except Exception as err:
            raise NormalizationError("speech_normalization_failure") from err

    def sanitize_text(self, text: str) -> str:
        """Sanitize text by normalizing, lowercasing, and removing unwanted characters."""
        normalized = unicodedata.normalize("NFKD", text.casefold())
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

        for separator in ("-", "_", "/"):
            ascii_text = ascii_text.replace(separator, " ")

        ascii_text = re.sub(r"[^a-z0-9 ]+", " ", ascii_text)
        ascii_text = re.sub(r"\s+", " ", ascii_text).strip()

        return ascii_text

    def correct_incongruences(self, text: str) -> str:
        """
        Correct common phrase and token incongruences based on configured mappings.
        
        Uses: 
            - self.phrase_corrections
            - self.token_corrections
            - and self.drop_tokens to clean up the text.
        """
        phrase_corrected = self.phrase_corrections.get(text, text)
        tokens: list[str] = []

        for token in phrase_corrected.split():
            if token in self.drop_tokens or self._should_drop_token(token):
                continue

            corrected = self.token_corrections.get(token, token)
            tokens.extend(corrected.split())

        return " ".join(tokens).strip()

    def map_to_canonical_command(self, text: str) -> str | None:
        """
        Tries to map the normalized text to a canonical command using configured aliases.
        
        Uses: 
            - self.command_aliases
        """
        return self.command_aliases.get(text)

    def resolve_fuzzy_candidate(self, text: str) -> str | None:
        """
        Tries to map the normalized text to a canonical command using configured aliases.
        
        Uses: 
            - self.fuzzy_candidates
            - self.fuzzy_score_cutoff
        """
        
        def _is_plausible_for_fuzzy(text: str) -> bool:
            """
            Check if the text is plausible for fuzzy matching based on length and token count.
            
            Uses: 
                - self.max_fuzzy_length
                - self.max_fuzzy_tokens
            """
            if text == "":
                return False
            
            if len(text) > self.max_fuzzy_length:
                return False
            
            if len(text.split()) > self.max_fuzzy_tokens:
                return False
            
            return True

        if not _is_plausible_for_fuzzy(text):
            return None

        match = process.extractOne(
            text,
            self.fuzzy_candidates,
            scorer=fuzz.ratio,
            score_cutoff=self.fuzzy_score_cutoff,
        )
        if match is None:
            return None

        best_candidate = match[0]
        return self.command_aliases.get(best_candidate, best_candidate)

    @staticmethod
    def _should_drop_token(token: str) -> bool:
        if len(token) == 1 and not token.isdigit():
            return True

        return len(set(token)) == 1 and len(token) > 2
