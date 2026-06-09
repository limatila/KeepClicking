# 003 — Create Domain Command Model

Status: `[COMPLETE]`

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

- Command model modules (shared enum choices plus command dataclasses).

## Implementation requirements

- Create `src/core/interfaces/choices.py` and define `class BaseChoice(str, Enum)` as a shared base for string enums, including helper methods for listing and resolving values.
- Create `src/core/choices.py` and define:
	- `class BaseCommandAction(BaseChoice)`
	- `class KeyboardCommandAction(BaseCommandAction)` as a reserved future extension point
	- `class MouseCommandAction(BaseCommandAction)` with values `STOP`, `CLICK`, `DOUBLE_CLICK`, `RIGHT_CLICK`, `SCROLL`, `MOVE`
	- `class CommandDirection(BaseChoice)` with values `UP`, `DOWN`, `LEFT`, `RIGHT`
- Create `src/core/dataclasses.py` and define:
	- `@dataclass class BaseCommand` with fields `action: BaseCommandAction` and `amount: int = 1`
	- `@dataclass class MouseCommand(BaseCommand)` with fields `action: MouseCommandAction`, `amount: int | None = None`, `direction: CommandDirection | None = None`
- `MouseCommand.__post_init__()` should fill default `amount` values from the active config defaults.
- Add a short class docstring to every enum and dataclass.
- Keep the model serializable and importable without side effects.

Pseudo-code summary:

```text
command = MouseCommand(action=MouseCommandAction.CLICK)
command = MouseCommand(action=MouseCommandAction.MOVE, direction=CommandDirection.LEFT, amount=50)
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
