# 009 — Implement Keyboard Input Adapter

Status: `[COMPLETE]`

## Purpose

Create a dev-only input adapter for debugging and testing without microphone usage.

## Context

- The automation pipeline should be testable without microphone usage during development.
- MVP activation is wake-word and speech recognition focused.
- Terminal input is dev-only and must not be used in production packages.

## Scope

- Read text commands from terminal input and send them through the same pipeline.
- Conform to the speech adapter interface from spec 008.

## Out of scope

- Speech recognition or microphone input.

## Inputs

- Typed text from the terminal.

## Outputs

- Recognized command text strings.

## Implementation requirements

- Create `src/speech/keyboard_adapter.py`.
- Define `class KeyboardSpeechAdapter` implementing `SpeechAdapter` with a short class docstring.
- Constructor:
	- `def __init__(self, prompt: str)`
- Method behavior:
	- `next_text()` uses `input(prompt)` and returns the string.
	- On `EOFError`, return `None` to signal end-of-stream.
	- If the user submits an empty string, return `""` and allow the runner to ignore it.
- `close()` is a no-op.
- Mark this adapter as dev-only in module docstring and README notes.

## Acceptance criteria

- The full pipeline can run using typed commands.

## Manual validation

- Type "click", "move right", and "stop" in the terminal.

## Dependencies

- `008-implement-speech-engine-interface.md` - path: `.github/specs/008-implement-speech-engine-interface.md`

## Reference to Next step

`016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`
