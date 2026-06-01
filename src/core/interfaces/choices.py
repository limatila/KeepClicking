"""Shared enum choices for core models."""

from enum import Enum


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