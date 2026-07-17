from src.core.choices import CommandDirection, MouseCommandAction


def test_mouse_command_action_prefers_more_specific_phrase_match():
    assert MouseCommandAction.resolve_choice_by_full_text("please double click now") == (
        MouseCommandAction.DOUBLE_CLICK
    )
    assert MouseCommandAction.resolve_choice_by_full_text("right click") == (
        MouseCommandAction.RIGHT_CLICK
    )


def test_mouse_command_action_uses_substring_matching_only():
    assert MouseCommandAction.resolve_choice_by_full_text("scroll") == MouseCommandAction.SCROLL
    assert MouseCommandAction.resolve_choice_by_full_text("move") == MouseCommandAction.MOVE


def test_command_direction_uses_broad_string_matching():
    assert CommandDirection.resolve_choice_by_full_text("move right now") == CommandDirection.RIGHT
    assert CommandDirection.resolve_choice_by_full_text("please scroll down") == CommandDirection.DOWN
