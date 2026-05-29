# 014 — Add Error Handling

Status: `[PLANNED]`

## Purpose

Make the app fail safely.

## Context

Mouse automation must avoid unsafe behavior on unknown or invalid input.

## Scope

Handle parser failures, validation failures, missing dependencies, and PyAutoGUI exceptions.

## Out of scope

No retry loops for unsafe commands.

## Inputs

Errors from all layers.

## Outputs

Safe failure messages and continued loop where appropriate.

## Implementation requirements

Unknown speech must not execute any action. Dependency errors must explain fallback.

## Acceptance criteria

Invalid input never reaches PyAutoGUI.

## Manual validation

Try unsupported commands and confirm no mouse action.

## Dependencies

013 — Add Logging

## Next step

015 — Add Tests
