# 003 — Create Domain Command Model

Status: `[PLANNED]`

## Purpose

Create the structured command representation used by the parser, validator, and mouse controller.

## Context

Raw text must not move directly into mouse execution.

## Scope

Define command types, actions, directions, and amount fields.

## Out of scope

No parsing logic. No PyAutoGUI calls.

## Inputs

Command contract reference spec.

## Outputs

Command model module.

## Implementation requirements

Use dataclass, enum, or typed model. Keep it simple and serializable.

## Acceptance criteria

Supported actions and directions match the command contract.

## Manual validation

Instantiate each command type in a Python shell or unit test.

## Dependencies

002 — Define Project Config

## Next step

004 — Implement Text Normalizer
