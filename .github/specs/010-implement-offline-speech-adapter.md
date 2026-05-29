# 010 — Implement Offline Speech Adapter

Status: `[PLANNED]`

## Purpose

Add the first offline speech-to-text adapter.

## Context

Offline-first recognition is preferred for cost, privacy, and reliability.

## Scope

Implement one offline adapter behind the speech engine interface.

## Out of scope

No online provider dependency. No direct mouse execution.

## Inputs

Microphone audio.

## Outputs

Recognized text.

## Implementation requirements

Keep dependencies isolated. Adapter must be optional if dependency is not installed.

## Acceptance criteria

Application can still run with keyboard adapter when speech dependency is unavailable.

## Manual validation

Speak a supported command and confirm recognized text enters the pipeline.

## Dependencies

009 — Implement Keyboard Input Adapter

## Next step

011 — Implement Application Runner
