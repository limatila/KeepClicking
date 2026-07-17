"""Shared command surface rules for parser, validator, and normalizers."""

from __future__ import annotations


from src.core.choices import CommandDirection, MouseCommandAction, CommandShape


_DECLARED_VALID_SHAPES: dict[MouseCommandAction, CommandShape] = {
    MouseCommandAction.SCROLL: CommandShape(
        action=MouseCommandAction.SCROLL,
        allowed_directions=(
            CommandDirection.UP,
            CommandDirection.DOWN,
        ),
        invalid_direction_reason="invalid_scroll_direction",
    ),
    MouseCommandAction.MOVE: CommandShape(
        action=MouseCommandAction.MOVE,
        allowed_directions=tuple(CommandDirection),
    ),
}


def _build_command_shapes() -> tuple[CommandShape, ...]:
    return tuple(
        _DECLARED_VALID_SHAPES.get(action, CommandShape(action=action))
        for action in MouseCommandAction
    )


COMMAND_SHAPES: tuple[CommandShape, ...] = _build_command_shapes()


def _validate_command_shapes() -> None:
    shapes_by_action = {shape.action: shape for shape in COMMAND_SHAPES}

    missing_actions = set(MouseCommandAction) - set(shapes_by_action)
    if missing_actions:
        raise ValueError(f"Missing command shapes configured: {missing_actions}")

    unknown_actions = set(shapes_by_action) - set(MouseCommandAction)
    if unknown_actions:
        raise ValueError(f"Unknown command shapes configured: {unknown_actions}")

    for shape in COMMAND_SHAPES:
        if shape.requires_direction and not shape.allowed_directions:
            raise ValueError(f"Directional action {shape.action.value} must declare directions")

        invalid_directions = set(shape.allowed_directions) - set(CommandDirection)
        if invalid_directions:
            raise ValueError(
                f"Invalid directions configured for {shape.action.value}: {invalid_directions}"
            )


_validate_command_shapes()


def get_command_shape(action: MouseCommandAction) -> CommandShape:
    """Return the configured standardized shape for an action."""

    for shape in COMMAND_SHAPES:
        if shape.action == action:
            return shape

    raise KeyError(f"Missing shape for action: {action.value}")


def iter_command_shapes() -> tuple[CommandShape, ...]:
    """Iterate over every configured standardized command shape."""

    return COMMAND_SHAPES
