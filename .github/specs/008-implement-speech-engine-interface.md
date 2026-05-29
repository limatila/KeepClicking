# 008 — Implement Speech Engine Interface

Status: `[PLANNED]`

## Purpose

Define a replaceable interface for speech recognition engines.

## Context

The project may use offline or optional online speech providers later.

## Scope

Create an abstract adapter interface returning recognized text.

## Out of scope

No provider-specific implementation. No PyAutoGUI calls.

## Inputs

Audio source or activation signal.

## Outputs

Recognized text string or empty result.

## Implementation requirements

Keep interface minimal. Avoid leaking provider-specific details.

## Acceptance criteria

Mock adapter can be implemented easily for tests.

## Manual validation

Create a fake adapter that returns `click`.

## Dependencies

007 — Implement Mouse Controller

## Next step

009 — Implement Keyboard Input Adapter
