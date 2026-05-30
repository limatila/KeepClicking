# 011 — Implement Application Runner

Status: `[COMPLETE]`

## Purpose

Wire the normalizer, parser, validator, speech adapter, and mouse controller together.

## Context

- The runner owns the execution loop for the speech-first MVP.
- The pipeline must remain modular as described in ../instructions/001-architecture-overview.instruction.md.

## Scope

- Create the loop that receives text, normalizes, parses, validates, executes, and stops on a stop command.
- Allow dependency injection of adapters and controllers for testing.

## Out of scope

- New command meanings.
- GUI or background daemon mode.
- Wake-word detection.

## Inputs

- Speech adapter (primary) or dev keyboard adapter.
- Normalizer, parser, validator, and mouse controller instances.

## Outputs

- Running local automation loop.

## Implementation requirements

- Keep each layer separate and loosely coupled.
- Errors should not crash the loop unnecessarily.
- Support a clean shutdown when a stop command is validated.
- Create `src/service/runner.py` with:
	- `class ApplicationRunner` and a short class docstring.
    - `def __init__(self, adapter: SpeechAdapter, normalizer: Callable[[str], str], parser: CommandParser, validator: CommandValidator, controller: MouseController, config: AppConfig, logger: logging.Logger)`
	- `def run(self) -> None`
- Loop semantics:
	- Call `adapter.next_text()`; if `None`, exit the loop.
	- Ignore empty strings.
	- Normalize text, parse, validate, then execute.
	- If `ExecutionResult.stopped` is `True`, exit the loop.
- Errors should not crash the loop unnecessarily. Use result objects and log errors.
- Support a clean shutdown by calling `adapter.close()` in a `finally` block.

Pseudo-code summary:

```python
while True:
    text = adapter.next_text()
    if text is None: break
    if text == "": continue
    normalized = normalizer(text)
    parse = parser.parse(normalized, config)
    if parse.command is None: continue
    valid = validator.validate(parse.command)
    if valid.command is None: continue
    result = controller.execute(valid.command, config)
    if result.stopped: break
```

## Acceptance criteria

- The speech adapter can run the full MVP flow with wake-word activation.
- The dev keyboard adapter can run the pipeline for debugging.

## Manual validation

- Start the runner, issue commands, then issue stop.

## Dependencies

- `010-implement-offline-speech-adapter.md` - path: `.github/specs/010-implement-offline-speech-adapter.md`

## Reference to Next step

`013-add-logging.md` - path: `.github/specs/013-add-logging.md`
