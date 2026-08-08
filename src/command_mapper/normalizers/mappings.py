"""Normalizer constants and language-specific catalogs."""

from __future__ import annotations

from collections.abc import Mapping

from src.command_mapper.command_shapes import iter_command_shapes
from src.core.choices import SpeechLanguage


def resolve_canonical_mapping() -> tuple[str, ...]:
    return tuple(
        phrase
        for command_shape in iter_command_shapes()
        for phrase in command_shape.canonical_phrases()
    )


CANONICAL_COMMANDS: tuple[str, ...] = resolve_canonical_mapping() # Ex: "click", "double click", "move up",

#* en-us
ENGLISH_DROP_TOKENS: frozenset[str] = frozenset(
    {"a", "an", "the", "please", "now", "just", "uh", "um"}
)

ENGLISH_PHRASE_CORRECTIONS: Mapping[str, str] = {
    "the were click": "double click",
    "were click": "double click",
    "doubleclick": "double click",
    "rightclick": "right click",
}

ENGLISH_TOKEN_CORRECTIONS: Mapping[str, str] = {
    "clique": "click",
    "clicks": "click",
}

ENGLISH_COMMAND_ALIASES: Mapping[str, str] = {
    "click": "click",
    "double click": "double click",
    "right click": "right click",
    "two click": "double click",
    "too click": "double click",
    "to click": "double click",
    "mouse up": "move up",
    "mouse down": "move down",
    "mouse left": "move left",
    "mouse right": "move right",
    "move up": "move up",
    "move down": "move down",
    "move left": "move left",
    "move right": "move right",
    "scroll up": "scroll up",
    "scroll down": "scroll down",
    "stop": "stop",
}

#* pt-br
PORTUGUESE_DROP_TOKENS: frozenset[str] = frozenset(
    {"o", "a", "os", "as", "por", "favor", "porfavor", "agora", "so", "um", "uma"}
)

PORTUGUESE_PHRASE_CORRECTIONS: Mapping[str, str] = {
    "clique duplo": "double click",
    "duplo clique": "double click",
    "clique direito": "right click",
    "botao direito": "right click",
    "botao esquerdo": "click",
    "rolar para cima": "scroll up",
    "rolar para baixo": "scroll down",
    "role para cima": "scroll up",
    "role para baixo": "scroll down",
    "mova para cima": "move up",
    "mova para baixo": "move down",
    "mova para esquerda": "move left",
    "mova para direita": "move right",
    "mexa para cima": "move up",
    "mexa para baixo": "move down",
    "mexa para esquerda": "move left",
    "mexa para direita": "move right",
    "pare": "stop",
    "para": "stop",
}

PORTUGUESE_TOKEN_CORRECTIONS: Mapping[str, str] = {
    "clicar": "click",
    "clique": "click",
    "direito": "right",
    "duplo": "double",
    "doble": "double",
    "mova": "move",
    "mover": "move",
    "mexa": "move",
    "suba": "up",
    "cima": "up",
    "baixo": "down",
    "esquerda": "left",
    "direita": "right",
    "rolar": "scroll",
    "role": "scroll",
    "parar": "stop",
}

PORTUGUESE_COMMAND_ALIASES: Mapping[str, str] = {
    "click": "click",
    "double click": "double click", 
    "right click": "right click",
    "scroll up": "scroll up",
    "scroll down": "scroll down",
    "move up": "move up",
    "move down": "move down",
    "move left": "move left",
    "move right": "move right",
    "stop": "stop",
}


def resolve_recognition_phrases(language: SpeechLanguage) -> tuple[str, ...]:
    """Return the speech phrases the recognizer should accept for one language."""

    if language == SpeechLanguage.PT_BR:
        return tuple(
            dict.fromkeys(
                (
                    *CANONICAL_COMMANDS,
                    *PORTUGUESE_COMMAND_ALIASES.keys(),
                    *PORTUGUESE_PHRASE_CORRECTIONS.keys(),
                    *PORTUGUESE_TOKEN_CORRECTIONS.keys(),
                )
            )
        )

    return tuple(
        dict.fromkeys(
            (
                *CANONICAL_COMMANDS,
                *ENGLISH_COMMAND_ALIASES.keys(),
                *ENGLISH_PHRASE_CORRECTIONS.keys(),
                *ENGLISH_TOKEN_CORRECTIONS.keys(),
            )
        )
    )
