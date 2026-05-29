---

name: GitHub Copilot Instructions - KeepClicking

---

# GitHub Copilot Instructions — KeepClicking

This repository follows Specification Driven Development (SDD).

Copilot must implement the project by reading the sequential specs in `specs/steps/` in numeric order.

## Source of truth order

1. `instructions/000-project-context.md`
2. `instructions/001-architecture-overview.md`
3. `instructions/002-command-contract.md`
4. `specs/000-status-tracker.md`
5. `specs/NNN-name-spec.md` in ascending numeric order

## Development rules

- Do not introduce a framework unless a spec requires it.
- Do not replace PyAutoGUI as the final mouse execution layer.
- Keep speech recognition replaceable behind an interface.
- Prefer offline-first speech recognition.
- Online speech-to-text providers may be added only as optional adapters.
- Each step must be independently readable.
- If a change affects architecture, add or update a spec before coding.

## Status markers

Use these exact markers:

- `[PENDING]`
- `[IN_PROGRESS]`
- `[COMPLETE]`
- `[INCOMPLETE]`

## Expected workflow

Before writing code:

1. Read the specs.
3. Read the status tracker.
4. Implement everything in accord with what specs are defining.
5. Add tests or manual validation notes defined by the spec.
6. Update the status tracker.

### Workflow rules

- Update the tracker after every end of request.
- Do not update the tracker before completing the implementation of the current steps in execution.

## Repository principle

The specs must allow Copilot to understand the project without relying on chat history.
