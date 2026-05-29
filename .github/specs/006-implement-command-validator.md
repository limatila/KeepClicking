# 006 — Implement Command Validator

Status: `[PLANNED]`

## Purpose

Validate parsed commands before execution.

## Context

Validation prevents unsupported or unsafe operations from reaching PyAutoGUI.

## Scope

Check action, direction, amount, and allowed command set.

## Out of scope

No raw text parsing. No PyAutoGUI calls.

## Inputs

Command object.

## Outputs

Validated command or validation error.

## Implementation requirements

Reject unknown actions, invalid directions, and negative amounts.

## Acceptance criteria

Invalid command objects cannot reach execution.

## Manual validation

Create invalid command objects and confirm rejection.

## Dependencies

005 — Implement Command Parser

## Next step

007 — Implement Mouse Controller
