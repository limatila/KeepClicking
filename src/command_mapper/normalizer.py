"""Text normalization utilities."""

from __future__ import annotations

import re

TOKEN_SYNONYM_MAP: dict[str, str] = {
    "clique": "click",
    "clicks": "click",
    "doubleclick": "double click",
    "the were click": "double click",
    "rightclick": "right click",
}


def normalize_text(raw_text: str) -> str:
    """Normalize raw text into a deterministic command-friendly string."""

    text = raw_text.lower().strip()

    for separator in ("-", "_", "/"):
        text = text.replace(separator, " ")

    text = re.sub(r"[^a-z0-9 ]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    normalized_tokens: list[str] = []
    for token in text.split():
        normalized_tokens.extend(
            TOKEN_SYNONYM_MAP.get(token, token).split()
        )

    return " ".join(normalized_tokens)
