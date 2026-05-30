# 006 — Implement Command Validator

Status: `[COMPLETE]`

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

- Create `src/commands/validator.py` with:
	- `@dataclass class ValidationError` with fields `reason: str` and `field: str | None`.
	- `@dataclass class ValidationResult` with fields:
		- `command: Command | None`
		- `error: ValidationError | None`
	- `class CommandValidator(Protocol)` with a short class docstring and method:
		- `def validate(self, command: Command) -> ValidationResult`
	- `class RuleBasedCommandValidator` implementing `CommandValidator` with a short class docstring.
- RuleBasedCommandValidator must reject unknown actions, invalid directions, and non-positive amounts.
- RuleBasedCommandValidator must ensure `direction` is only present for `move` and `scroll` actions.
- RuleBasedCommandValidator must ensure `direction` is `None` for `click`, `double_click`, `right_click`, and `stop`.
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

## Dependencies

- `005-implement-command-parser.md` - path: `.github/specs/005-implement-command-parser.md`

## Reference to Next step

`007-implement-mouse-controller.md` - path: `.github/specs/007-implement-mouse-controller.md`
