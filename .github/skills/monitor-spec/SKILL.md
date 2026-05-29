---

name: monitor-spec
description: Use this skill to check the repo implementation progress against the SDD specs.
argument-hint: "Provide details about the spec to monitor, or call the agent to review all specs implemented in repo."

---

# Skill: monitor-spec

Use this skill to check implementation progress against the SDD specs.
This skill explain how to track, monitor, and write in spec files the current state of implementation, checking out every spec that already has been implemented.


## Goal

Compare the repository code with `specs/` and `specs/000-status-tracker.md`.

## Spec statuses
Statuses to use: `[PENDING]`, `[IN PROGRESS]`, `[COMPLETE]`, `[INCOMPLETE]`

## Checks

- Confirm sequential steps are implemented (not necessarily in order, adjust to complete all when needed).
- Confirm each completed step has evidence in code or tests.
- Stablish a contract with the spec, always checking if the implementation is drifting from the spec, and report any drift to the User (and change the state in `000-status-tracker.md` to `[INCOMPLETE]`).
- Confirm a spec file is updated with the current status of implementation.
- Confirm any drift from spec is reported and explained in the spec file.

## Output

Report:

- Completed specs
- In-progress specs
- Blocked specs
- Drift from spec
- Suggested next implementation step
