---

name: create-spec
description: Use this skill when adding a new implementation step, or modifying existing ones if asked by the User.
argument-hint: "Inform details of a new spec. You can specify a existing spec to modify."
apply-to: .github/specs/*.md

---

# Skill: create-spec

Use this skill when adding a new implementation step, or modifying existing ones if asked by the User.

## Goal

Create one small, sequential, implementation-ready spec file.

## Required format

Each spec must contain:

1. Title
2. Status
3. Purpose
4. Context
5. Scope
6. Out of scope
7. Inputs
8. Outputs
9. Implementation requirements
10. Acceptance criteria
11. Manual validation
12. Dependencies
13. Reference to Next step

## Naming

Use this pattern:

`NNN-short-action-name.md`

Example:

`006-implement-command-parser.md`

## Basic Rules

- A spec should describe one implementable step only.
- All specs shall be respected, unless a future created spec explicitly states that it replaces or changes a previous one.
- A new spec that overides the implementation of a previous spec must explicitly reference the previous one and explain the differences and reasons for the change (you can argue with the User to explain and inform them before implementation).


## Details about format
- **Title**: Clear, concise title of the spec.
- **Status**: Pending, In Progress, Completed, Tested.
- **Purpose**: Why this spec is needed.
- **Context**: Background information and reference to related specs and instructions files inside `.github/`.
- **Scope**: What is included in this spec.
- **Out of scope**: What is explicitly not included in this spec.
- **Inputs**: What inputs are required for this implementation step.
- **Outputs**: What outputs are expected from this implementation step.
- **Implementation requirements**: Specific technical requirements, techonologies involved, abstractions used, technical debts to be addressed, etc.
- **Acceptance criteria**: Clear, testable and observable criteria that must be met for the implementation to be considered complete.
- **Manual validation**: Steps for manually validating the implementation.

### Must explicitely include references:
- **Dependencies**: Other specs that must be completed before this one can be implemented.
- **Reference to Next step**: A reference to the next spec that should be implemented after this one, if applicable.

Reference shall be a fast format including the name and fullpath to the spec file, for example:

`007-implement-command-parser.md` - path: `.github/skills/create-spec/specs/007-implement-command-parser.md`
and more information if considered necessary.
