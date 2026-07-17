"""Shared enum choices for core models."""

from __future__ import annotations

from enum import Enum
from typing import Self


class BaseChoice(str, Enum):
    """Base class for string enums used across the domain models."""

    @classmethod
    def list_choices_values(cls, exclude: list[str] = []) -> list[str]:
        return [
            choice.value for choice in cls
            if str(choice.value) not in exclude
        ]

    @classmethod
    def get_choice_by_value(cls, value_to_find: str):
        value_to_find = value_to_find.strip().lower()

        for choice in cls:
            if choice.value == value_to_find:
                return choice

        return None

    @classmethod
    def resolve_choice_by_full_text(cls, text: str) -> Self | None:
        
        def _normalize_choice_text(choice_value: str) -> str:
            return choice_value.strip().lower().replace("_", " ")
        
        normalized_text = text.strip().lower()

        for choice in sorted(
            cls, key=lambda item: (-len(_normalize_choice_text(item.value)), _normalize_choice_text(item.value)),
        ):
            if _normalize_choice_text(choice.value) in normalized_text:
                return choice

        return None
