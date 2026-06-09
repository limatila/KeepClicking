# 007 — Implement Mouse Controller

Status: `[COMPLETE]`

## Purpose

Execute validated mouse actions through PyAutoGUI.

## Context

- PyAutoGUI is the accepted backend for mouse operations.
- Architecture rule: only the Mouse Controller may import and call PyAutoGUI.

## Scope

- Implement click, double click, right click, scroll, move, and stop handling.
- Apply configuration values for movement, scroll amounts, and safety pause.

## Out of scope

- Speech recognition.
- Raw text parsing or validation.

## Inputs

- Validated command object.
- Configuration values from spec 002.

## Outputs

- Mouse action executed or stop signal returned.

## Implementation requirements

- Create `src/service/dataclasses.py` with `@dataclass class MouseExecutionResult`.
- Create `src/service/interfaces.py` with `class Controller(Protocol)` and method `def execute(self, command: MouseCommand, config: AppConfig) -> MouseExecutionResult`.
- Create `src/service/hardware_controller.py` with `class PyAutoGuiMouseController` implementing `Controller`.
- Only this module may import PyAutoGUI.
- Set `pyautogui.PAUSE` and `pyautogui.FAILSAFE` using `AppConfig` values during execution.
- PyAutoGuiMouseController command-to-call mapping:
	- `CLICK` -> repeated `pyautogui.click()` based on `command.amount`
	- `DOUBLE_CLICK` -> repeated `pyautogui.click()` based on `command.amount`
	- `RIGHT_CLICK` -> repeated `pyautogui.rightClick()` based on `command.amount`
	- `SCROLL` + `UP` -> `pyautogui.scroll(command.amount)`
	- `SCROLL` + `DOWN` -> `pyautogui.scroll(-command.amount)`
	- `MOVE` + `UP` -> `pyautogui.moveRel(0, -command.amount)`
	- `MOVE` + `DOWN` -> `pyautogui.moveRel(0, command.amount)`
	- `MOVE` + `LEFT` -> `pyautogui.moveRel(-command.amount, 0)`
	- `MOVE` + `RIGHT` -> `pyautogui.moveRel(command.amount, 0)`
	- `STOP` -> return `MouseExecutionResult(stopped=True, error=None)` without calling PyAutoGUI

Pseudo-code summary:

```text
result = controller.execute(command, config)
if result.stopped:
		exit_loop()
```

## Acceptance criteria

- Each command maps to the intended PyAutoGUI call.
- Safety pause and failsafe settings are applied.

## Manual validation

- Run in a safe desktop environment and test simple movement and click commands.

## Dependencies

- `006-implement-command-validator.md` - path: `.github/specs/006-implement-command-validator.md`

## Reference to Next step

`008-implement-speech-engine-interface.md` - path: `.github/specs/008-implement-speech-engine-interface.md`
