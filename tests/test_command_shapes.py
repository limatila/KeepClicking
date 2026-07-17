from src.command_mapper.command_shapes import get_command_shape, iter_command_shapes
from src.core.choices import CommandDirection, MouseCommandAction


def test_every_mouse_action_has_a_resolved_command_shape():
    resolved_actions = {
        command_shape.action
        for command_shape in iter_command_shapes()
    }

    assert resolved_actions == set(MouseCommandAction)


def test_directional_shapes_follow_registered_rules():
    scroll_shape = get_command_shape(MouseCommandAction.SCROLL)
    move_shape = get_command_shape(MouseCommandAction.MOVE)

    assert scroll_shape.requires_direction is True
    assert scroll_shape.allowed_directions == (
        CommandDirection.UP,
        CommandDirection.DOWN,
    )
    assert scroll_shape.invalid_direction_reason == "invalid_scroll_direction"

    assert move_shape.requires_direction is True
    assert move_shape.allowed_directions == tuple(CommandDirection)


def test_non_directional_shapes_are_resolved_automatically():
    click_shape = get_command_shape(MouseCommandAction.CLICK)

    assert click_shape.requires_direction is False
    assert click_shape.allowed_directions == ()


def test_command_shape_exposes_canonical_phrases_and_direction_logic():
    scroll_shape = get_command_shape(MouseCommandAction.SCROLL)
    click_shape = get_command_shape(MouseCommandAction.CLICK)

    assert scroll_shape.canonical_phrases() == (
        "scroll up",
        "scroll down",
    )
    assert click_shape.canonical_phrases() == ("click",)
    assert scroll_shape.resolve_direction_by_text("please scroll down now") == CommandDirection.DOWN
    assert click_shape.resolve_direction_by_text("click") is None
    assert scroll_shape.validate_direction(CommandDirection.LEFT) == "invalid_scroll_direction"
    assert click_shape.validate_direction(CommandDirection.UP) == "direction_not_applicable"
