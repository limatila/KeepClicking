# 017 - Package Local Runner Preparation

Status: `[COMPLETE]`

## Purpose

Prepare and validate the first production packaging target for local use.

## Context

- Production runs through `src/main.py`.
- `src/cli.py` is a dev-only harness and is excluded from production packaging.
- Production packages must not show a terminal window.
- Installer wrapping is deferred; the first MVP artifact is a local windowed PyInstaller EXE.

## Scope

- Build a Windows windowed executable from `src/main.py`.
- Bundle runtime model resources.
- Keep dev/test/cache/repository files out of the production artifact.
- Document development setup separately from production packaging.

## Out of scope

- MSI/installer EXE wrapping.
- Linux deb packaging.
- App store packaging.

## Inputs

- Automated-test-validated MVP.
- Runtime resources under `src/resources/models`.

## Outputs

- `dist/KeepClicking.exe`
- `scripts/build_exe.ps1`
- Updated README production/development sections.
- Updated validation checklist and package smoke results.

## Implementation requirements

- Follow ADR decision in `021-adr-packaging-toolchain.md`: use PyInstaller.
- Build from `src/main.py` with windowed mode.
- Include only the default production model data:
	- `src/resources/models/openwakeword/hey_keeper_v2.onnx`
	- `src/resources/models/openwakeword/melspectrogram.onnx`
	- `src/resources/models/openwakeword/embedding_model.onnx`
	- `src/resources/models/vosk/vosk-model-small-en-us-0.15`
- Collect Vosk package binaries/data so `vosk/libvosk.dll` is available where Vosk's loader expects it.
- Use `packaging/hooks/hook-sklearn.py` to omit non-runtime sklearn dataset/test data from the PyInstaller artifact.
- Exclude production-irrelevant files and modules:
	- `.venv`, `.cache`, `.tmp_pytest`, `.pytest_cache`
	- `.gitignore`, `.python-version`, `pytest.ini`, `rewrite-email.ps1`, `uv.lock`
	- `tests/`, `.vscode/`, `.agents/`, `.github/`
	- `src/cli.py`
	- `pytest`, `faker`, `pyinstaller`, and other dev-only dependencies
- Keep development dependencies in `[dependency-groups].dev`.

Portable build command:

```powershell
.\scripts\build_exe.ps1
```

## Acceptance criteria

- `uv run pytest` passes.
- `uv run python -m src.main -h` exits successfully.
- `uv run python -m src.main --list-audio-devices` exits successfully.
- `dist/KeepClicking.exe -h` exits successfully.
- `dist/KeepClicking.exe --list-audio-devices` exits successfully.
- Production executable is windowed and built from `src/main.py`.
- Archive inspection finds no forbidden project/dev paths, old wake-word model, PT Vosk model, or sklearn dataset test data.
- Archive inspection confirms `vosk/libvosk.dll` is bundled.

## Manual validation

- Automated tests: pass, 86 passed on 2026-07-20.
- Production entrypoint smokes: pass on 2026-07-20.
- Packaged executable smokes: pass by exit code on 2026-07-20.
- Archive exclusion check: pass on 2026-07-20.
- Packaged startup check: pass on 2026-07-20; windowed EXE stayed alive and reached wake-word listening.
- Live speech/manual mouse pass is tracked by spec 016 and remains a human validation step.

## Dependencies

- `016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`
- `015-add-tests.md` - path: `.github/specs/015-add-tests.md`
- `018-adr-offline-speech-engine-selection.md` - path: `.github/specs/018-adr-offline-speech-engine-selection.md`
- `021-adr-packaging-toolchain.md` - path: `.github/specs/021-adr-packaging-toolchain.md`

## Reference to Next step

Future specs may add installer wrapping, Linux packaging, GUI, macros, or online adapters.
