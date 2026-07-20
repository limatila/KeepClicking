# 001 — Initialize Repository

Status: `[COMPLETE]`

## Purpose

Create the initial Python repository layout for KeepClicking.

## Context

- Align with project goals and MVP constraints in ../instructions/000-project-context.instruction.md.
- Align with modular architecture expectations in ../instructions/001-architecture-overview.instruction.md.

## Scope

- Establish the Python package layout under `src/`.
- Create package submodules for core, command mapping, speech, service, and wake-word support.
- Create a `tests/` package for unit tests.

## Out of scope

- Business logic, parsing, or validation behavior.
- Speech recognition or PyAutoGUI usage.
- Configuration values (handled in spec 002).

## Inputs

- Existing .github docs and specs.

## Outputs

- Repository skeleton with `src/`, `tests/`, `pyproject.toml`, and `.gitignore`.
- Minimal module files required by downstream specs.

## Implementation requirements

- Use a `src/` layout with `src/__init__.py`.
- Create the following package structure (empty modules only, with short module docstrings):
	- `src/__init__.py`
	- `src/main.py` (production entrypoint)
	- `src/cli.py` (dev-only harness)
	- `src/core/config.py`
	- `src/core/choices.py`
	- `src/core/dataclasses.py`
	- `src/core/interfaces/__init__.py`
	- `src/core/interfaces/choices.py`
	- `src/core/errors.py`
	- `src/core/logging.py`
	- `src/command_mapper/normalizer.py`
	- `src/command_mapper/parser.py`
	- `src/command_mapper/validator.py`
	- `src/command_mapper/interfaces.py`
	- `src/command_mapper/dataclasses.py`
	- `src/speech/interfaces.py`
	- `src/speech/keyboard_adapter.py`
	- `src/speech/offline_vosk_adapter.py`
	- `src/speech/wakeword/engine.py`
	- `src/service/application_runner.py`
	- `src/service/hardware_controller.py`
	- `src/service/interfaces.py`
	- `src/service/dataclasses.py`
- Create `tests/__init__.py`.
- Every module created should include a short module docstring. Classes introduced in later specs must include a brief class docstring.

Creation summary:

Create package directories and placeholder modules only.
No functional logic in this spec.

## Acceptance criteria

- A local import works with `PYTHONPATH=src`.
- Project structure is clear and ready for sequential specs.

## Manual validation

- Run `PYTHONPATH=src python -c "import src; print(src.__name__)"`.

## Dependencies

- None.

## Reference to Next step

`002-define-project-config.md` - path: `.github/specs/002-define-project-config.md`
