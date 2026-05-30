# 002 — Define Project Config

Status: `[COMPLETE]`

## Purpose

Define runtime configuration defaults for movement, scrolling, and safety, and expose a typed configuration object for the MVP pipeline.

## Context

- Mouse movement and scroll amounts require central configuration.
- MVP activation is wake-word + speech recognition focused.
- Terminal debugging is dev-only and must not be the default production path.
- Architecture favors explicit defaults over hidden values per ../instructions/001-architecture-overview.instruction.md.

## Scope

- Create a configuration module with defaults for movement pixels, scroll units, and safety pause.
- Include a speech-first input mode default and dev-only keyboard option.
- Add wake-word defaults and offline speech placeholders without implementing persistence.

## Out of scope

- Persistent configuration storage.
- Environment variable overrides or UI settings.

## Inputs

- Repository skeleton from spec 001.

## Outputs

- A configuration module with explicit defaults and a typed config object.

## Implementation requirements

- Create `src/core/config.py`.
- Define `InputMode` as a `str` enum with at least:
	- `SPEECH_OFFLINE = "speech_offline"`
	- `KEYBOARD_DEV = "keyboard_dev"`
- Define `AppConfig` as a dataclass with explicit defaults:
	- `input_mode: InputMode = InputMode.SPEECH_OFFLINE`
	- `move_pixels: int = 50`
	- `scroll_units: int = 300`
	- `pyautogui_pause_seconds: float = 0.1`
	- `pyautogui_failsafe: bool = True`
	- `wake_word_phrase: str = "keeper"`
	- `wake_word_listen_seconds: float = 5.0`
	- `keyboard_prompt: str = "keepclicking> "`
	- `offline_model_path: str | None = None`
- Provide `def get_config(base: AppConfig | None = None, **overrides) -> AppConfig` that returns defaults when `base` is `None`, otherwise returns a copy with overrides.
- Add short class docstrings to `InputMode` and `AppConfig` describing their purpose.

Pseudo-code summary:

```text
config = get_config()
config = get_config(config, move_pixels=100)
```

## Acceptance criteria

- Other modules can import configuration values and `AppConfig`.
- Defaults are unit-testable and stable.

## Manual validation

- Run a Python shell and print the config values to verify defaults.

## Dependencies

- `001-initialize-repository.md` - path: `.github/specs/001-initialize-repository.md`
- `019-adr-wake-word-engine-selection.md` - path: `.github/specs/019-adr-wake-word-engine-selection.md`
- `020-adr-gui-deferred.md` - path: `.github/specs/020-adr-gui-deferred.md`

## Reference to Next step

`003-create-domain-command-model.md` - path: `.github/specs/003-create-domain-command-model.md`
