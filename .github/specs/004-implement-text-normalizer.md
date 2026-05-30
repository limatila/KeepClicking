# 004 — Implement Text Normalizer

Status: `[COMPLETE]`

## Purpose

Normalize recognized text before parsing to ensure deterministic command matching.

## Context

- Speech engines may return inconsistent casing, spacing, punctuation, or accents.
- Normalization must align with the command phrases in ../instructions/002-command-contract.instruction.md.

## Scope

- Lowercase input, trim whitespace, and collapse repeated spaces.
- Remove irrelevant punctuation and normalize separators (for example, "double-click" -> "double click").
- Map simple synonyms (for example, "clique" -> "click") when safe.

## Out of scope

- Command parsing or validation.
- Language detection beyond simple synonym mapping.

## Inputs

- Raw recognized text from a speech or keyboard adapter.

## Outputs

- Normalized text string.

## Implementation requirements

- Create `src/commands/normalizer.py`.
- Implement a pure function:
	- `def normalize_text(raw_text: str) -> str`
- Normalization steps (deterministic order):
	- lowercase
	- trim leading/trailing whitespace
	- replace `-`, `_`, and `/` with spaces
	- remove punctuation except alphanumerics and spaces
	- collapse repeated whitespace into a single space
- Maintain a small `SYNONYM_MAP` dict (for example, `{ "clique": "click" }`).
- Add a short docstring to `normalize_text` describing the intent.

Pseudo-code summary:

```text
text = normalize_text("  Double-Click ")  # "double click"
```

## Acceptance criteria

- Common inputs normalize consistently and deterministically.

## Manual validation

- Test examples like " Click ", "double-click", and "clique".

## Dependencies

- `003-create-domain-command-model.md` - path: `.github/specs/003-create-domain-command-model.md`

## Reference to Next step

`005-implement-command-parser.md` - path: `.github/specs/005-implement-command-parser.md`
