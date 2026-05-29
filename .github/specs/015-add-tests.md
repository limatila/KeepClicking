# 015 — Add Tests

Status: `[PLANNED]`

## Purpose

Add automated tests for deterministic layers.

## Context

Parser, normalizer, validator, and command models should be testable without desktop automation.

## Scope

Create unit tests for normalizer, parser, validator, config, and runner using mocks.

## Out of scope

No live microphone tests. No real mouse movement in automated tests.

## Inputs

Source modules.

## Outputs

Test suite.

## Implementation requirements

Mock PyAutoGUI for controller tests. Avoid moving the real mouse in CI.

## Acceptance criteria

Tests pass locally.

## Manual validation

Run the test command and confirm all tests pass.

## Dependencies

014 — Add Error Handling

## Next step

016 — Manual MVP Validation
