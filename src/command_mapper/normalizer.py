"""Text normalization utilities."""

from __future__ import annotations

import re

SYNONYM_MAP: dict[str, str] = {
	"clique": "click",
}


def normalize_text(raw_text: str) -> str:
	"""Normalize raw text into a deterministic command-friendly string."""

	text = raw_text.lower().strip()
	
	for separator in ("-", "_", "/"):
		text = text.replace(separator, " ")
	
	text = re.sub(r"[^a-z0-9 ]+", "", text)
	text = re.sub(r"\s+", " ", text).strip()
	
	return SYNONYM_MAP.get(text, text)
