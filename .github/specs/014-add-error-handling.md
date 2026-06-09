# 014 — Add Error Handling

Status: `[COMPLETE]`

## Purpose

Make the app fail safely.

## Context

- Mouse automation must avoid unsafe behavior on unknown or invalid input.
- The runner should remain stable during recoverable errors.

## Scope

- Handle parser failures, validation failures, missing dependencies, and PyAutoGUI exceptions.
- Provide safe failure messages and keep the loop alive where appropriate.

## Out of scope

- Automatic retries for unsafe commands.
- Background recovery processes.

## Inputs

- Errors from all layers.

## Outputs

- Safe failure messages and continued loop where appropriate.

## Implementation requirements

- Create `src/core/errors.py` with:
	- `class ApplicationError(Exception)` as the current base class with a short docstring
	- `class MouseExecutionError(ApplicationError)` for PyAutoGUI failures
	- `class AdapterError(ApplicationError)` for input adapter failures
	- `class ValidationError(Exception)` carrying `reason` and `field`
- Parser and validator must use result objects and must not raise exceptions for expected failures, except for validator rule methods that raise `ValidationError` internally and are converted into result objects.
- The runner catches `ApplicationError` and logs the message without exiting the loop (unless `stop` is requested).
- Unknown speech must not execute any action.
- Adapter errors must explain the failure clearly enough for local debugging.
- Exceptions from PyAutoGUI must be caught and reported safely.
- Make sure existing processes uses the Exceptions pattern for error handling, and refactor if necessary to align with this approach.

Pseudo-code summary:

```text
try:
		result = controller.execute(command, config)
except MouseExecutionError as exc:
		logger.error("mouse_error", extra={"error": str(exc)})
```

## Acceptance criteria

- Invalid input never reaches PyAutoGUI.
- The runner continues after recoverable errors.
- Existing implementations use the Exceptions pattern

## Manual validation

- Try unsupported commands and confirm no mouse action occurs.

## Dependencies

- `013-add-logging.md` - path: `.github/specs/013-add-logging.md`

## Reference to Next step

`009-implement-keyboard-input-adapter.md` - path: `.github/specs/009-implement-keyboard-input-adapter.md`
