# 011 — Implement Application Runner

Status: `[PLANNED]`

## Purpose

Wire normalizer, parser, validator, speech adapter, and mouse controller together.

## Context

The runner owns the execution loop.

## Scope

Create the loop that receives text, parses, validates, executes, and stops on stop command.

## Out of scope

No new command meanings. No GUI.

## Inputs

Speech/input adapter and controller.

## Outputs

Running local automation loop.

## Implementation requirements

Each layer must remain separate. Errors should not crash the loop unnecessarily.

## Acceptance criteria

Typed adapter can run the full MVP flow.

## Manual validation

Start runner, issue commands, issue stop.

## Dependencies

010 — Implement Offline Speech Adapter

## Next step

012 — Implement CLI Entrypoint
