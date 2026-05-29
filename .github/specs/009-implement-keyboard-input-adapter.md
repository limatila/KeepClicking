# 009 — Implement Keyboard Input Adapter

Status: `[PLANNED]`

## Purpose

Create a temporary input adapter for development without speech recognition.

## Context

The automation pipeline should be testable before microphone integration.

## Scope

Read text commands from CLI input and send them through the same pipeline.

## Out of scope

No actual speech recognition.

## Inputs

Typed text from terminal.

## Outputs

Recognized command text.

## Implementation requirements

Use the same speech engine interface shape if possible.

## Acceptance criteria

The full pipeline can run using typed commands.

## Manual validation

Type `click`, `move right`, and `stop` in the terminal.

## Dependencies

008 — Implement Speech Engine Interface

## Next step

010 — Implement Offline Speech Adapter
