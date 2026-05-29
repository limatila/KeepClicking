# 003 — Create Domain Command Model

Status: `[PENDING]`

## Purpose

Create the structured command representation used by the parser, validator, and mouse controller.

## Context

- Raw text must not move directly into mouse execution.
- The command contract in ../instructions/002-command-contract.instruction.md defines supported actions and fields.
- The architecture overview recommends dataclasses and enums for commands.

## Scope

- Define command actions, directions, and amount fields.
- Provide a serializable command model for downstream layers.

## Out of scope

- Parsing logic.
- PyAutoGUI calls or execution logic.

## Inputs

- Command contract instruction file.
- Configuration defaults from spec 002.

## Outputs

- Command model module (enums plus command dataclass).

## Implementation requirements

- Create `src/core/models.py` and define:
	- `class BaseChoice(str, Enum)` as a shared base for string enums.
	- `class CommandAction(BaseChoice)` with values:
		- `CLICK = "click"`
		- `DOUBLE_CLICK = "double_click"`
		- `RIGHT_CLICK = "right_click"`
		- `SCROLL = "scroll"`
		- `MOVE = "move"`
		- `STOP = "stop"`
	- `class CommandDirection(BaseChoice)` with values:
		- `UP = "up"`, `DOWN = "down"`, `LEFT = "left"`, `RIGHT = "right"`
	- `@dataclass class Command` with fields:
		- `action: CommandAction`
		- `amount: int = 1`
		- `direction: CommandDirection | None = None`
- Add a short class docstring to every enum and dataclass.
- Keep the model serializable and importable without side effects.

Pseudo-code summary:

```text
command = Command(action=CommandAction.CLICK)
command = Command(action=CommandAction.MOVE, direction=CommandDirection.LEFT, amount=1)
```

## Acceptance criteria

- Supported actions and directions match the command contract.
- Command objects can be instantiated with defaults and validated downstream.

## Manual validation

- Instantiate each command type in a Python shell or unit test.

## Dependencies

- `002-define-project-config.md` - path: `.github/specs/002-define-project-config.md`

## Reference to Next step

`004-implement-text-normalizer.md` - path: `.github/specs/004-implement-text-normalizer.md`
