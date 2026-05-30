# 005 — Implement Command Parser

Status: `[COMPLETE]`

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
- Config defaults from `AppConfig`.

## Outputs

- Parse result containing either a command or a parse error.

## Implementation requirements

- Create `src/commands/parser.py` with:
	- `@dataclass class ParseError` with fields `reason: str` and `raw_text: str`.
	- `@dataclass class ParseResult` with fields:
		- `command: Command | None`
		- `error: ParseError | None`
	- `class CommandParser(Protocol)` with a short class docstring and method:
		- `def parse(self, text: str, config: AppConfig) -> ParseResult`
	- `class RuleBasedCommandParser` implementing `CommandParser` with a short class docstring.
- Deterministic parsing only; no probabilistic matching.
- RuleBasedCommandParser must map the normalized phrases:
	- "click" -> `Command(action=CommandAction.CLICK)`
	- "double click" -> `Command(action=CommandAction.DOUBLE_CLICK, amount=2)`
	- "right click" -> `Command(action=CommandAction.RIGHT_CLICK)`
	- "scroll up" -> `Command(action=CommandAction.SCROLL, direction=UP, amount=config.scroll_units)`
	- "scroll down" -> `Command(action=CommandAction.SCROLL, direction=DOWN, amount=config.scroll_units)`
	- "move up" -> `Command(action=CommandAction.MOVE, direction=UP, amount=config.move_pixels)`
	- "move down" -> `Command(action=CommandAction.MOVE, direction=DOWN, amount=config.move_pixels)`
	- "move left" -> `Command(action=CommandAction.MOVE, direction=LEFT, amount=config.move_pixels)`
	- "move right" -> `Command(action=CommandAction.MOVE, direction=RIGHT, amount=config.move_pixels)`
	- "stop" -> `Command(action=CommandAction.STOP)`
- Unknown phrases must return `ParseResult(command=None, error=ParseError(...))` and never produce a command.

Pseudo-code summary:

```text
result = parser.parse(normalized, config)
if result.command is None:
		handle_parse_error(result.error)
```

## Acceptance criteria

- All MVP commands parse correctly.
- Unknown phrases do not produce executable commands.

## Manual validation

- Manually parse all command contract examples.

## Dependencies

- `004-implement-text-normalizer.md` - path: `.github/specs/004-implement-text-normalizer.md`

## Reference to Next step

`006-implement-command-validator.md` - path: `.github/specs/006-implement-command-validator.md`
