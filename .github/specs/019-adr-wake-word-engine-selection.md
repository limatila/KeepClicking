# 019 - ADR: Wake Word Engine Selection

Status: `[COMPLETE]`

## Purpose

Select the wake-word engine for the MVP speech-first pipeline.

## Context

- MVP requires wake-word activation with offline capability.
- The repository includes OpenWakeWord as a dependency.
- Wake-word detection must be low-latency and suitable for continuous listening.

## Scope

- Decide which wake-word engine is used for MVP.
- Record implications for adapter implementation.

## Out of scope

- Implementing the wake-word adapter.
- Training or tuning custom models.

## Inputs

- Engine comparison: latency, resource usage, offline viability, licensing.

## Outputs

- Decision statement and consequences for specs.

## Implementation requirements

- Comparison summary:
  - OpenWakeWord: offline, lightweight, designed for always-on detection, compatible with MVP requirements.
  - Alternatives: not evaluated for MVP unless a dependency change is required.
- Decision: Use OpenWakeWord for MVP wake-word detection.
- Consequences:
  - Speech adapter integrates OpenWakeWord for wake-word detection.
  - Optional fallback remains dev keyboard adapter only.

## Acceptance criteria

- Decision is recorded with a clear rationale.
- Spec 010 references this ADR.

## Manual validation

- Review the decision with the user and mark status once approved.

## Dependencies

- None.

## Reference to Next step

`018-adr-offline-speech-engine-selection.md` - path: `.github/specs/018-adr-offline-speech-engine-selection.md`
