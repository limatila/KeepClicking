# 015 — Add Tests

Status: `[COMPLETE]`

## Purpose

Add automated tests for deterministic layers.

## Context

- Parser, normalizer, validator, and command models should be testable without desktop automation.
- Tests must not move the real mouse.
- Pytest is available in project dependencies.
- Tests are implemented and executed only after all functional specs are complete.
- DO NOT implement/write/add or execute tests until all non-test specs are complete. FOLLOW THIS STRICTELY

## Scope

- Unit tests for normalizer, parser, validator, config, and runner using mocks.
- Mock PyAutoGUI in controller tests.

## Out of scope

- Live microphone tests.
- Real mouse movement in automated tests.

## Inputs

- Source modules.

## Outputs

- Test suite.

## Implementation requirements

- Use `pytest` for tests.
- Create tests:
	- `tests/test_normalizer.py`
	- `tests/test_parser.py`
	- `tests/test_validator.py`
	- `tests/test_config.py`
	- `tests/test_mouse_controller.py`
	- `tests/test_runner.py`
- Mock `pyautogui` calls using `unittest.mock` to ensure no real mouse movement.
- Provide a fake `SpeechAdapter` for runner tests.

Pseudo-code summary:

```text
def test_parser_click():
		result = parser.parse("click", config)
		assert result.command.action == CommandAction.CLICK
```

## Acceptance criteria

- Tests pass locally.
- No test triggers real mouse movement.

## Manual validation

- Run the test command and confirm all tests pass.

## Dependencies

- `014-add-error-handling.md` - path: `.github/specs/014-add-error-handling.md`
- `016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`

## Reference to Next step

`021-adr-packaging-toolchain.md` - path: `.github/specs/021-adr-packaging-toolchain.md`
