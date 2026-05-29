# 008 — Implement Speech Engine Interface

Status: `[PENDING]`

## Purpose

Define a replaceable interface for input adapters that provide recognized text.

## Context

- Offline-first recognition is preferred, but engines must remain replaceable.
- MVP is speech-first with wake-word activation.
- Dev-only keyboard input remains a fallback for testing and debugging.

## Scope

- Create a minimal adapter interface that returns recognized text.
- Define a minimal wake-word engine interface used by speech adapters.
- Define a simple lifecycle for closing the adapter.

## Out of scope

- Provider-specific implementations.
- Concrete wake-word detection behavior.
- PyAutoGUI calls.

## Inputs

- Audio source or activation signal (as defined by adapter implementations).

## Outputs

- Recognized text string or `None` when the adapter has no more input.

## Implementation requirements

- Create `src/speech/interfaces.py`.
- Define a protocol or abstract base class:
	- `class InputAdapter(Protocol)` with a short class docstring.
	- `def next_text(self) -> str | None` returning recognized text or `None` on end-of-stream.
	- `def close(self) -> None` for cleanup (no-op allowed).
- Define a protocol:
	- `class WakeWordEngine(Protocol)` with a short class docstring.
	- `def wait_for_wake_word(self) -> bool` returning `True` when the wake word is detected.
- Keep the interfaces minimal and provider-agnostic.
- Avoid leaking engine-specific configuration through the interfaces.
- Allow a simple mock adapter for tests.

Pseudo-code summary:

```text
if wake_word_engine.wait_for_wake_word():
	text = adapter.next_text()
	if text is None:
		stop_loop()
```

## Acceptance criteria

- A mock adapter can be implemented with a single method that returns text.

## Manual validation

- Create a fake adapter that returns "click" and confirm the runner consumes it.

## Dependencies

- `007-implement-mouse-controller.md` - path: `.github/specs/007-implement-mouse-controller.md`

## Reference to Next step

`019-adr-wake-word-engine-selection.md` - path: `.github/specs/019-adr-wake-word-engine-selection.md`
