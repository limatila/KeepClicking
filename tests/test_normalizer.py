from src.command_mapper.normalizers.english import EnglishSpeechNormalizer
from src.command_mapper.command_shapes import iter_command_shapes
from src.command_mapper.normalizers.mappings import (
    CANONICAL_COMMANDS,
    ENGLISH_COMMAND_ALIASES,
    PORTUGUESE_COMMAND_ALIASES,
    resolve_canonical_mapping,
)
from src.command_mapper.normalizers.portuguese import PortugueseSpeechNormalizer
from src.command_mapper.normalizer_dispatchers import resolve_command_normalizer
from src.core.choices import SpeechLanguage


def test_normalize_click():
    assert EnglishSpeechNormalizer().normalize(" Click ") == "click"


def test_normalize_double_click_separator_cleanup():
    assert EnglishSpeechNormalizer().normalize("double-click") == "double click"


def test_normalize_known_vosk_phrase_incongruence():
    assert EnglishSpeechNormalizer().normalize("the were click") == "double click"


def test_normalize_noisy_mouse_alias():
    assert EnglishSpeechNormalizer().normalize("a mouse up") == "move up"


def test_normalize_unicode_and_noise_cleanup():
    assert EnglishSpeechNormalizer().normalize("aaa!!! clique???") == "click"


def test_normalize_portuguese_command_to_canonical_english():
    assert PortugueseSpeechNormalizer().normalize("clique duplo") == "double click"


def test_normalize_portuguese_directional_command():
    assert PortugueseSpeechNormalizer().normalize("mova para esquerda") == "move left"


def test_canonical_commands_are_generated_from_mappings_catalog():
    assert CANONICAL_COMMANDS == resolve_canonical_mapping()
    assert CANONICAL_COMMANDS == (
        "stop",
        "click",
        "double click",
        "right click",
        "scroll up",
        "scroll down",
        "move up",
        "move down",
        "move left",
        "move right",
    )

    for command_shape in iter_command_shapes():
        spoken_action = command_shape.normalized_value

        if not command_shape.requires_direction:
            assert spoken_action in CANONICAL_COMMANDS
            continue

        assert spoken_action not in CANONICAL_COMMANDS
        for phrase in command_shape.canonical_phrases():
            assert phrase in CANONICAL_COMMANDS


def test_normalizer_fuzzy_candidates_only_include_valid_canonical_commands():
    english_normalizer = EnglishSpeechNormalizer()
    portuguese_normalizer = PortugueseSpeechNormalizer()

    for canonical_command in CANONICAL_COMMANDS:
        assert canonical_command in english_normalizer.fuzzy_candidates
        assert canonical_command in portuguese_normalizer.fuzzy_candidates

    assert "scroll" not in CANONICAL_COMMANDS
    assert "move" not in CANONICAL_COMMANDS


def test_language_alias_targets_only_point_to_canonical_commands():
    canonical_commands = set(CANONICAL_COMMANDS)

    assert set(ENGLISH_COMMAND_ALIASES.values()).issubset(canonical_commands)
    assert set(PORTUGUESE_COMMAND_ALIASES.values()).issubset(canonical_commands)


def test_resolve_normalizer_by_language():
    assert isinstance(
        resolve_command_normalizer(SpeechLanguage.EN_US),
        EnglishSpeechNormalizer,
    )
    assert isinstance(
        resolve_command_normalizer(SpeechLanguage.PT_BR),
        PortugueseSpeechNormalizer,
    )
