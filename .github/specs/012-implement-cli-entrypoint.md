# 012 — Implement CLI Entrypoint

Status: `[PLANNED]`

## Purpose

Expose the application through a command-line entrypoint.

## Context

The MVP needs a simple local execution path.

## Scope

Add CLI options for input mode and safe defaults.

## Out of scope

No graphical interface. No daemon service.

## Inputs

User CLI invocation.

## Outputs

Running KeepClicking session.

## Implementation requirements

Support at least keyboard mode. Speech mode may be conditional.

## Acceptance criteria

User can start the program from terminal.

## Manual validation

Run the CLI and execute a full command loop.

## Dependencies

011 — Implement Application Runner

## Next step

013 — Add Logging
