# 004 — Implement Text Normalizer

Status: `[PLANNED]`

## Purpose

Normalize recognized speech text before parsing.

## Context

Speech engines may return inconsistent casing, spacing, punctuation, or accents.

## Scope

Create a normalizer that lowercases, trims whitespace, removes irrelevant punctuation, and maps simple synonyms.

## Out of scope

No command execution. No validation.

## Inputs

Raw recognized text.

## Outputs

Normalized text string.

## Implementation requirements

Support English command phrases first. Optional Portuguese synonyms may be included.

## Acceptance criteria

Common inputs normalize consistently.

## Manual validation

Test examples like ` Click `, `double-click`, `clique`.

## Dependencies

003 — Create Domain Command Model

## Next step

005 — Implement Command Parser
