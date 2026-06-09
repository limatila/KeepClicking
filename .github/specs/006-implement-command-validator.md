# 006 — Implement Command Validator

Status: `[INCOMPLETE]`

## Purpose

Validate parsed commands before execution.

## Context

- Validation prevents unsupported or unsafe operations from reaching PyAutoGUI.
- Commands must align with the contract in ../instructions/002-command-contract.instruction.md.

## Scope

- Check action, direction, and amount fields.
- Enforce allowed action and direction combinations.

## Out of scope

- Raw text parsing.
- PyAutoGUI calls or execution.

## Inputs

- Command object from the parser.

## Outputs

- Validation result containing either a validated command or a validation error.

## Implementation requirements

- Create `src/command_mapper/dataclasses.py` with `@dataclass class ValidationResult`.
- Use `ValidationError` from `src/core/errors.py`.
- Create `src/command_mapper/interfaces.py` with `class CommandValidator` base behavior and method `def validate(self, command: BaseCommand) -> ValidationResult`.
- Create `src/command_mapper/validator.py` with `class MouseCommandValidator` implementing the current MVP rules.
- `MouseCommandValidator` must reject:
	- actions that are not instances of `MouseCommandAction`
	- negative amounts
	- `move` commands without a direction
	- `move` commands whose direction is not a `CommandDirection`
	- non-`move` commands that still carry a direction
- Validation must be deterministic and side-effect free.

Pseudo-code summary:

```text
result = validator.validate(command)
if result.command is None:
    handle_validation_error(result.error) #placed always in a abstraction
```

## Acceptance criteria

- Invalid command objects cannot reach execution.
- Valid commands pass through without modification.

## Manual validation

- Create invalid command objects and confirm rejection.

Current drift:
The validator wiring exists, but the current rules still allow `scroll` commands without a direction and accept zero-amount non-stop commands.

## Dependencies

- `005-implement-command-parser.md` - path: `.github/specs/005-implement-command-parser.md`

## Reference to Next step

`007-implement-mouse-controller.md` - path: `.github/specs/007-implement-mouse-controller.md`
