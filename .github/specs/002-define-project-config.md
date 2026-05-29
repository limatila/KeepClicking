# 002 — Define Project Config

Status: `[PLANNED]`

## Purpose

Define runtime configuration defaults.

## Context

Mouse movement and scroll amounts need central configuration.

## Scope

Create a configuration module with defaults for movement pixels, scroll units, recognition mode, and safety pause.

## Out of scope

No environment loading beyond simple defaults. No UI settings screen.

## Inputs

Project skeleton.

## Outputs

Configuration object or module.

## Implementation requirements

Keep values explicit and documented. Avoid hidden magic numbers in command execution.

## Acceptance criteria

Other modules can import config values. Defaults are testable.

## Manual validation

Print or inspect config values from a Python shell.

## Dependencies

001 — Initialize Repository

## Next step

003 — Create Domain Command Model
