# 016 — Manual MVP Validation

Status: `[INCOMPLETE]`

## Purpose

Validate the MVP manually in a real desktop environment.

## Context

- Automated tests should not perform real mouse movement.
- Manual validation ensures the end-to-end pipeline works safely.

## Scope

- Create a checklist for speech-first mode (wake word + offline speech).
- Include a dev-only keyboard checklist for debugging.

## Out of scope

- New implementation features.
- GUI testing (future capability).

## Inputs

- Built MVP speech pipeline (wake-word + offline speech + runner).

## Outputs

- Manual validation report or checklist completion record.

## Implementation requirements

- Create `docs/validation/mvp-checklist.md` with the following sections:
	- Environment (OS, Python version)
	- Input mode (speech_offline or keyboard_dev)
	- Commands tested (list each MVP command)
	- Pass/fail per command
	- Notes/issues
- Include both keyboard and speech sections, marking speech as optional if dependencies are unavailable.

Pseudo-code summary:

```text
Checklist:
- click: pass/fail
- double click: pass/fail
... etc
```

## Acceptance criteria

- Every MVP command has a pass/fail result.

## Manual validation

- Complete the checklist on the development machine.

Current drift:
The checklist template exists, but the repository does not yet include a filled validation record.

## Dependencies

- `010-implement-offline-speech-adapter.md` - path: `.github/specs/010-implement-offline-speech-adapter.md`
- `011-implement-application-runner.md` - path: `.github/specs/011-implement-application-runner.md`
- `013-add-logging.md` - path: `.github/specs/013-add-logging.md`
- `014-add-error-handling.md` - path: `.github/specs/014-add-error-handling.md`

## Reference to Next step

`015-add-tests.md` - path: `.github/specs/015-add-tests.md`
