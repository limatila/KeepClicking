# MVP Package Local Runner

Status: `[COMPLETE]`

## Purpose

Track the final local production packaging execution work that follows the numbered implementation specs and ADRs.

## Context

- Users should be able to run a production artifact without a terminal window.
- The production runtime entrypoint is `src/main.py`.
- `src/cli.py` is a dev-only harness and is excluded from production packaging.
- This file is the umbrella follow-up after spec 017 and ADR 021.

## Scope

- Produce first-stage local Windows production executables.
- Document production packaging separately from development setup.
- Keep speech resources bundled under production runtime resources.
- Keep language/model defaults bundled per executable.
- Exclude repository, dev, test, and cache files from production packaging.

## Out of scope

- MSI/installer EXE wrapping.
- Linux deb packaging.
- App store packaging.

## Inputs

- Automated-test-validated MVP.
- Packaging toolchain decision from ADR 021.
- Runtime models under `src/resources/models`.

## Outputs

- `dist/KeepClicking-en-us.exe`
- `dist/KeepClicking-pt-br.exe`
- `scripts/build_exe.ps1`
- `packaging/env/en-us/packaged.env`
- `packaging/env/pt-br/packaged.env`
- README production/development documentation.
- Packaging and validation records in `.github/specs` and `docs/validation`.

## Implementation requirements

- Use PyInstaller in windowed one-file mode.
- Build from `src/main.py`, not `src/cli.py`.
- Build separate `en-us` and `pt-br` EXEs so each package carries only its matching Vosk model.
- Bundle OpenWakeWord production model resources in both packages.
- Bundle a packaged production env in each EXE so language defaults are baked in but external `.env` overrides remain possible beside the EXE.
- Collect Vosk package binaries/data so `vosk/libvosk.dll` is available where Vosk's loader expects it.
- Use `packaging/hooks/hook-sklearn.py` to omit non-runtime sklearn dataset/test data.
- Keep OpenWakeWord support assets as production resources:
	- `src/resources/models/openwakeword/melspectrogram.onnx`
	- `src/resources/models/openwakeword/embedding_model.onnx`
- In production (`debug_mode=false`), write logs per run as `run_N.log` files under `~/Documents/keepclicking_logs`, with writable fallbacks if needed.
- Exclude from production artifacts:
	- `.venv`, `.cache`, `.tmp_pytest`, `.pytest_cache`
	- `.gitignore`, `.python-version`, `pytest.ini`, `rewrite-email.ps1`, `uv.lock`
	- `tests/`, `.vscode/`, `.agents/`, `.github/`
	- `src/cli.py`
	- dev-only dependencies such as `pytest`, `faker`, and `pyinstaller`

Portable build command:

```powershell
.\scripts\build_exe.ps1
```

## Acceptance criteria

- `uv run pytest`: pass.
- `uv run python -m src.main -h`: pass.
- `uv run python -m src.main --list-audio-devices`: pass.
- `dist/KeepClicking-en-us.exe -h`: pass by exit code.
- `dist/KeepClicking-en-us.exe --list-audio-devices`: pass by exit code.
- `dist/KeepClicking-pt-br.exe -h`: pass by exit code.
- `dist/KeepClicking-pt-br.exe --list-audio-devices`: pass by exit code.
- Production packages start from `src/main.py` and are windowed.
- Archive inspection finds no forbidden project/dev paths, old wake-word model, or sklearn dataset test data.
- The `en-us` package excludes the PT Vosk model; the `pt-br` package excludes the EN Vosk model.
- Archive inspection confirms `vosk/libvosk.dll` is bundled.

## Manual validation

- Packaging validation completed on July 26, 2026.
- Final EXE sizes:
	- `KeepClicking-en-us.exe`: 138,430,388 bytes
	- `KeepClicking-pt-br.exe`: 129,668,477 bytes
- Packaged startup/logging check: pass on July 26, 2026. Both EXEs exited cleanly for `-h` and `--list-audio-devices`, and production logs were created as `run_N.log`.
- Live speech/manual mouse validation is tracked separately in spec 016 and still requires a human desktop pass.

## Dependencies

- `016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`
- `015-add-tests.md` - path: `.github/specs/015-add-tests.md`
- `017-package-local-runner.md` - path: `.github/specs/017-package-local-runner.md`
- `018-adr-offline-speech-engine-selection.md` - path: `.github/specs/018-adr-offline-speech-engine-selection.md`
- `021-adr-packaging-toolchain.md` - path: `.github/specs/021-adr-packaging-toolchain.md`

## Reference to Next step

Future specs may add installer wrapping, Linux packaging, GUI, macros, or online adapters.
