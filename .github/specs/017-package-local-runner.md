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

- Build Windows windowed executables from `src/main.py`.
- Bundle runtime model resources.
- Bundle language-specific production defaults with the packaged app.
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

- `dist/KeepClicking-en-us.exe`
- `dist/KeepClicking-pt-br.exe`
- `scripts/build_exe.ps1`
- `packaging/env/en-us/packaged.env`
- `packaging/env/pt-br/packaged.env`
- Updated README production/development sections.
- Updated validation checklist and package smoke results.

## Implementation requirements

- Follow ADR decision in `021-adr-packaging-toolchain.md`: use PyInstaller.
- Build from `src/main.py` with windowed mode.
- Produce separate EXEs for `en-us` and `pt-br`.
- Include OpenWakeWord production runtime data in both packages:
	- `src/resources/models/openwakeword/hey_keeper_v2.onnx`
	- `src/resources/models/openwakeword/melspectrogram.onnx`
	- `src/resources/models/openwakeword/embedding_model.onnx`
- Include only the matching Vosk model per EXE:
	- `dist/KeepClicking-en-us.exe` bundles `src/resources/models/vosk/vosk-model-small-en-us-0.15`
	- `dist/KeepClicking-pt-br.exe` bundles `src/resources/models/vosk/vosk-model-small-pt-0.3`
- Bundle a packaged production env per EXE so language/model defaults are baked in while still allowing external `.env` overrides beside the EXE.
- Collect Vosk package binaries/data so `vosk/libvosk.dll` is available where Vosk's loader expects it.
- Use `packaging/hooks/hook-sklearn.py` to omit non-runtime sklearn dataset/test data from the PyInstaller artifact.
- In production (`debug_mode=false`), write runtime logs to per-run files under `~/Documents/keepclicking_logs`, with fallback to another writable local path if needed.
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

Single-variant build commands:

```powershell
.\scripts\build_exe.ps1 -Variant en-us
.\scripts\build_exe.ps1 -Variant pt-br
```

## Acceptance criteria

- `uv run pytest` passes.
- `uv run python -m src.main -h` exits successfully.
- `uv run python -m src.main --list-audio-devices` exits successfully.
- `dist/KeepClicking-en-us.exe -h` exits successfully.
- `dist/KeepClicking-en-us.exe --list-audio-devices` exits successfully.
- `dist/KeepClicking-pt-br.exe -h` exits successfully.
- `dist/KeepClicking-pt-br.exe --list-audio-devices` exits successfully.
- Production executables are windowed and built from `src/main.py`.
- Archive inspection finds no forbidden project/dev paths, old wake-word model, or sklearn dataset test data.
- The `en-us` package excludes the PT Vosk model; the `pt-br` package excludes the EN Vosk model.
- Archive inspection confirms `vosk/libvosk.dll` is bundled.

## Manual validation

- Automated tests: pass, 89 passed on July 26, 2026.
- Production entrypoint smokes: pass on July 26, 2026.
- Packaged executable smokes: pass by exit code on July 26, 2026 for `KeepClicking-en-us.exe` and `KeepClicking-pt-br.exe`.
- Archive exclusion check: pass on July 26, 2026. The `en-us` package contains only the EN Vosk model; the `pt-br` package contains only the PT Vosk model; both include `packaged.env` and `vosk/libvosk.dll`.
- Packaged startup/logging check: pass on July 26, 2026. Production runs created `run_N.log` files. On this Windows machine, `~/Documents` was unavailable, so the runtime correctly fell back to `%TEMP%\\KeepClicking\\keepclicking_logs`.
- Live speech/manual mouse pass is tracked by spec 016 and remains a human validation step.

## Dependencies

- `016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`
- `015-add-tests.md` - path: `.github/specs/015-add-tests.md`
- `018-adr-offline-speech-engine-selection.md` - path: `.github/specs/018-adr-offline-speech-engine-selection.md`
- `021-adr-packaging-toolchain.md` - path: `.github/specs/021-adr-packaging-toolchain.md`

## Reference to Next step

Future specs may add installer wrapping, Linux packaging, GUI, macros, or online adapters.
