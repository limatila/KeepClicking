# 010 — Implement Offline Speech Adapter

Status: `[COMPLETE]`

## Purpose

Add the first offline speech-to-text adapter.

## Context

- Offline-first recognition is preferred for cost, privacy, and reliability.
- The preferred engine order is Vosk, then Whisper.cpp (or faster-whisper), then native APIs.
- Selecting the initial engine requires an ADR per project policy.

## Scope

- Implement one offline adapter behind the speech engine interface.
- Integrate wake-word detection before transcribing speech.
- Keep the adapter optional so the dev keyboard adapter remains usable without extra dependencies.

## Out of scope

- Online speech providers.
- Wake-word detection or continuous listening.
- Direct mouse execution.

## Inputs

- Microphone audio from the selected offline engine.

## Outputs

- Recognized text.

## Implementation requirements

- Follow ADR decision in `018-adr-offline-speech-engine-selection.md`.
- Create `src/speech/offline_vosk_adapter.py`.
- Define `class VoskSpeechAdapter` implementing `SpeechAdapter` with a short class docstring.
- Constructor:
	- `def __init__(self, config: AppConfig, wake_word_engine: WakeWordEngine)`
	- Use `config.offline_model_path` if provided.
- `next_text()` behavior:
	- Block until `wake_word_engine.wait_for_wake_word()` returns `True`.
	- Capture audio for up to `config.wake_word_listen_seconds`.
	- Return recognized text or an empty string if no speech is captured.
	- Return `None` on end-of-stream or unrecoverable adapter failure.
- Implement the wake-word engine using OpenWakeWord per ADR 019 in `src/wakeword/detector.py` as `OpenWakeWordEngine` implementing `WakeWordEngine`.
- Use `sounddevice` for microphone capture.
- Add the selected engine dependency (Vosk) to `pyproject.toml` if it is not already present.
- All optional dependencies must be imported lazily. On missing dependency, raise `OptionalDependencyError` from `core/errors.py` with a clear message.
- Keep dependencies isolated: dev keyboard mode must work without speech dependencies installed.

Pseudo-code summary:

```text
adapter = VoskSpeechAdapter(config)
text = adapter.next_text()
```

## Acceptance criteria

- Application can still run with the keyboard adapter when the speech dependency is missing.
- When the offline adapter is available, recognized text enters the pipeline.

## Manual validation

- Speak a supported command and confirm recognized text enters the pipeline.

## Dependencies

- `002-define-project-config.md` - path: `.github/specs/002-define-project-config.md`
- `008-implement-speech-engine-interface.md` - path: `.github/specs/008-implement-speech-engine-interface.md`
- `018-adr-offline-speech-engine-selection.md` - path: `.github/specs/018-adr-offline-speech-engine-selection.md`
- `019-adr-wake-word-engine-selection.md` - path: `.github/specs/019-adr-wake-word-engine-selection.md`

## Reference to Next step

`011-implement-application-runner.md` - path: `.github/specs/011-implement-application-runner.md`
