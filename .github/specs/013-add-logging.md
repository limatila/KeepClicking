# 013 — Add Logging

Status: `[COMPLETE]`

## Purpose

Add structured logging for development and debugging.

## Context

- Mouse automation errors and recognition failures need traceability.
- Logging must stay lightweight to preserve performance goals.

## Scope

- Log recognized text (after normalization), parsed command, validation errors, and execution results.
- Provide log levels suitable for debugging and normal operation.

## Out of scope

- Telemetry or remote logging.
- Logging raw audio data.

## Inputs

- Pipeline events from the runner.

## Outputs

- Local log output (console or file).

## Implementation requirements

- Create `src/core/logging.py` with preconfigured module loggers.
- Use the standard library `logging` module.
- Configure a base logger namespace named `baseLogger` and child loggers:
	- `baseLogger.core`
	- `baseLogger.adapter`
	- `baseLogger.runner`
	- `baseLogger.parser`
	- `baseLogger.validator`
	- `baseLogger.controller`
- Ensure modules use the child loggers derived from `baseLogger`.
- Do not log sensitive audio or high-volume data.
- Keep log volume low by default.

Pseudo-code summary:

```text
CORE_LOGGER.info("runner_started")
```

## Acceptance criteria

- Pipeline behavior can be diagnosed from logs.
- Logging does not noticeably degrade performance.

## Manual validation

- Run commands and inspect log output.

## Dependencies

- `011-implement-application-runner.md` - path: `.github/specs/011-implement-application-runner.md`

## Reference to Next step

`014-add-error-handling.md` - path: `.github/specs/014-add-error-handling.md`
