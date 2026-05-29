# 018 - ADR: Offline Speech Engine Selection

Status: `[PENDING]`

## Purpose

Select the initial offline speech engine for the MVP adapter.

## Context

- Offline-first recognition is required for privacy and reliability.
- Instruction priority order is Vosk, then Whisper.cpp (or faster-whisper), then native APIs.
- MVP targets low CPU usage and long-running stability.

## Scope

- Decide which offline engine to implement first.
- Record implications for dependencies and adapter naming.

## Out of scope

- Implementing the adapter itself.
- Benchmarking beyond a brief comparison.

## Inputs

- Engine comparison: latency, resource usage, offline viability, licensing.

## Outputs

- Decision statement and consequences for specs.

## Implementation requirements

- Comparison summary:
  - Vosk: light CPU, smaller models, fully offline, permissive licensing, good for long-running low CPU targets.
  - faster-whisper (Whisper.cpp/ctranslate2): higher accuracy, larger models, heavier CPU/GPU usage, still offline but higher resource cost.
- Decision: Use Vosk for the first offline adapter to match the documented priority order and low-resource MVP goals.
- Consequences:
  - Spec 010 should implement `offline_vosk_adapter.py`.
  - faster-whisper remains an optional alternative for a future spec.

## Acceptance criteria

- Decision is recorded with a clear rationale.
- Spec 010 references this ADR.

## Manual validation

- Review the decision with the user and mark status once approved.

## Dependencies

- None.

## Reference to Next step

`010-implement-offline-speech-adapter.md` - path: `.github/specs/010-implement-offline-speech-adapter.md`
