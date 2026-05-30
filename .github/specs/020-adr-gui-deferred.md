# 020 - ADR: GUI Deferred for MVP

Status: `[COMPLETE]`

## Purpose

Record the decision to defer any GUI for the MVP.

## Context

- MVP success criteria require a lightweight, reliable speech-first experience.
- The architecture supports future UI, but it is not required for initial delivery.

## Scope

- Declare that the MVP has no GUI.
- Define how GUI dependencies are treated.

## Out of scope

- Implementing a GUI.
- Selecting UI frameworks beyond documenting the deferral.

## Inputs

- Project MVP constraints and architecture priorities.

## Outputs

- Decision statement and implications for specs and dependencies.

## Implementation requirements

- Decision: MVP has no GUI; no PySide6 UI in this phase.
- Production packages must not display a terminal window.
- GUI dependencies must be treated as optional and unused in MVP code paths.
- Any GUI work must be introduced via a new spec.

## Acceptance criteria

- Spec 002 references this ADR for dev-only terminal decisions.

## Manual validation

- Confirm no MVP code path requires GUI dependencies.

## Dependencies

- None.

## Reference to Next step

`002-define-project-config.md` - path: `.github/specs/002-define-project-config.md`
