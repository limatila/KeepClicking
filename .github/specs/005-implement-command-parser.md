# 005 — Implement Command Parser

Status: `[PLANNED]`

## Purpose

Convert normalized text into command objects.

## Context

The parser is the boundary between text and structured automation intent.

## Scope

Map supported phrases to command model objects.

## Out of scope

No PyAutoGUI calls. No microphone code.

## Inputs

Normalized text.

## Outputs

Command object or parse failure result.

## Implementation requirements

Implement deterministic parsing. Unknown phrases must fail safely.

## Acceptance criteria

All MVP commands parse correctly. Unknown phrases do not execute.

## Manual validation

Manually parse all command contract examples.

## Dependencies

004 — Implement Text Normalizer

## Next step

006 — Implement Command Validator
