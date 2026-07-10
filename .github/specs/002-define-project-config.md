# 002 — Define Project Config

Status: `[COMPLETE]`

## Purpose

Define runtime configuration defaults for movement, scrolling, wake-word behavior, and safety, and expose a typed configuration object for the MVP pipeline.

## Context

- Mouse movement and scroll amounts require central configuration.
- MVP activation is wake-word + speech recognition focused.
- Terminal debugging is dev-only and must not be the default production path.
- Architecture favors explicit defaults over hidden values per ../instructions/001-architecture-overview.instruction.md.

## Scope

- Create a configuration module with defaults for movement pixels, scroll units, wake-word settings, and PyAutoGUI safety values.
- Load configuration values from `.env` when present while preserving code defaults.
- Expose helper functions for copying config with overrides.

## Out of scope

- Persistent configuration storage.
- Environment variable overrides or UI settings.

## Inputs

- Repository skeleton from spec 001.

## Outputs

- A configuration module with explicit defaults and a typed config object.

## Implementation requirements

- Create `src/core/config.py`.
- Define `AppConfig` as a dataclass with explicit defaults:
	- `debug_mode: bool`
	- `openwakeword_model_path: str`
	- `mouse_movement_pixels: int = 50`
	- `mouse_scroll_units: int = 300`
	- `pyautogui_pause_seconds: float = 0.1`
	- `pyautogui_failsafe: bool | None`
	- `wake_word_phrase: str = "keeper"`
	- `wake_word_listen_seconds: float = 5.0`
	- `offline_model_path: str | None = None`
	- `audio_input_device: str | None = None`
- Provide `get_env_or_default(key: str, default: str) -> str` for `.env`-backed values.
- Provide `def get_config(base: AppConfig | None = AppConfig(), **overrides) -> AppConfig` that returns the current config object when `overrides` are absent and a copied dataclass when overrides are provided.
- Add a short class docstring to `AppConfig` describing its purpose.

Pseudo-code summary:

```text
config = get_config()
config = get_config(config, mouse_movement_pixels=100, audio_input_device="USB")
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
