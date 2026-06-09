# 005 — Implement Command Parser

Status: `[INCOMPLETE]`

## Purpose

Convert normalized text into command objects.

## Context

- The parser is the boundary between text and structured automation intent.
- Inputs must match the command contract in ../instructions/002-command-contract.instruction.md.

## Scope

- Map supported phrases to command model objects.
- Provide a safe "no match" result for unknown phrases.

## Out of scope

- PyAutoGUI calls or execution.
- Microphone access or speech recognition.

## Inputs

- Normalized text string from the text normalizer.

## Outputs

- Parse result containing either a command or a parse error.

## Implementation requirements

- Create `src/command_mapper/dataclasses.py` with:
	- `@dataclass class ParseError` with fields `reason: str` and `raw_text: str`
	- `@dataclass class ParseResult` with fields `command: MouseCommand | None` and `error: ParseError | None`
- Create `src/command_mapper/interfaces.py` with `class CommandParser(Protocol)` and method `def parse(self, text: str) -> ParseResult`.
- Create `src/command_mapper/parser.py` with `class MouseCommandParser` implementing `CommandParser`.
- Deterministic parsing only; no probabilistic matching.
- `MouseCommandParser` should:
	- scan normalized text for the first `MouseCommandAction` value contained in the input
	- create `MouseCommand(action=...)` once an action token is found
	- resolve `CommandDirection` only when the parsed action is `MOVE`
	- return `ParseError(reason="missing_command_direction", raw_text=text)` when a `move` command has no direction token
	- return `ParseError(reason="unrecognized_command", raw_text=text)` when no action token is found
- Amount defaults come from `MouseCommand.__post_init__()` and are not injected by the parser.

Pseudo-code summary:

```text
result = parser.parse(normalized)
if result.command is None:
		handle_parse_error(result.error)
```

## Acceptance criteria

- All MVP commands parse correctly.
- Unknown phrases do not produce executable commands.

## Manual validation

- Manually parse all command contract examples.

Current drift:
The parser implementation exists in the documented module layout, but `double click` and `right click` currently collapse to `click`, and scroll commands do not yet carry parsed directions.

## Dependencies

- `004-implement-text-normalizer.md` - path: `.github/specs/004-implement-text-normalizer.md`

## Reference to Next step

`006-implement-command-validator.md` - path: `.github/specs/006-implement-command-validator.md`
