# 016 - Manual MVP Validation

Status: `[INCOMPLETE]`

## Purpose

Validate the MVP in a real desktop environment and keep a validation record under `docs/validation/mvp-checklist.md`.

## Context

- Automated tests must not perform real mouse movement.
- Automated validation now covers parser, validator, runner wiring, audio-device resolution, wake-word support asset resolution, Vosk adapter behavior, and PyAutoGUI calls with mocks.
- Live speech/manual mouse validation still requires a human desktop pass with microphone input and a safe mouse target.

## Scope

- Maintain a validation checklist for speech-first mode.
- Include production entrypoint and packaged executable smoke checks.
- Keep dev-only CLI checks separate from production validation.

## Out of scope

- GUI testing.
- App store or installer validation.

## Inputs

- Built MVP speech pipeline using `src/main.py`.
- Dev-only harness in `src/cli.py`.
- Packaged local executable in `dist/KeepClicking.exe`.

## Outputs

- `docs/validation/mvp-checklist.md` records:
	- Environment and Python version.
	- Production and packaged smoke checks.
	- Current model/resource paths.
	- Pass/fail state for every MVP command.
	- Explicit live speech/manual mouse status.

## Implementation requirements

- Keep `docs/validation/mvp-checklist.md` aligned with the code defaults:
	- Wake phrase: `hey keeper`
	- Wake-word model: `src/resources/models/openwakeword/hey_keeper_v2.onnx`
	- Wake-word listen window: `3.0` seconds
	- Movement: `200` pixels
	- Scroll: `350` units
	- Audio input: system default when `audio_input_device` is unset
- Mark automated command-path coverage separately from live speech/manual mouse validation.

## Acceptance criteria

- Every MVP command has an automated command-path pass/fail result.
- Live speech/manual mouse status is recorded honestly.
- Spec remains incomplete until a human completes the live speech/manual mouse pass.

## Manual validation

- Automated preflight completed on 2026-07-20: `uv run pytest` passed with 86 tests.
- Production module smokes completed on 2026-07-20.
- Packaged executable smokes completed on 2026-07-20.
- Live speech/manual mouse validation: not run in this agent session.

## Dependencies

- `010-implement-offline-speech-adapter.md` - path: `.github/specs/010-implement-offline-speech-adapter.md`
- `011-implement-application-runner.md` - path: `.github/specs/011-implement-application-runner.md`
- `013-add-logging.md` - path: `.github/specs/013-add-logging.md`
- `014-add-error-handling.md` - path: `.github/specs/014-add-error-handling.md`

## Reference to Next step

`017-package-local-runner.md` - path: `.github/specs/017-package-local-runner.md`
