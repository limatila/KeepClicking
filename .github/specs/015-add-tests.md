# 015 — Add Tests

Status: `[INCOMPLETE]`

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
	- `tests/test_audio_device_resolver.py`
	- `tests/test_offline_vosk_adapter.py`
	- `tests/test_wakeword_engine.py`
- Mock `pyautogui` calls using `unittest.mock` to ensure no real mouse movement.
- Provide a fake speech adapter for runner tests.

Pseudo-code summary:

```text
def test_parser_click():
		result = parser.parse("click")
		assert result.command.action == MouseCommandAction.CLICK
```

## Acceptance criteria

- Tests should pass locally from the project virtualenv.
- No test triggers real mouse movement.

## Manual validation

- Run the test command and confirm all tests pass.
- Current drift: the suite exists, but at least one config expectation is out of sync with `.env`, so this step remains incomplete until the tests are brought back to green.

## Dependencies

- `014-add-error-handling.md` - path: `.github/specs/014-add-error-handling.md`
- `016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`

## Reference to Next step

`021-adr-packaging-toolchain.md` - path: `.github/specs/021-adr-packaging-toolchain.md`
