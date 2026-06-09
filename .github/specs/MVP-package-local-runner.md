# MVP Package Local Runner

Status: `[PENDING]`

## Purpose

Track the final packaging execution work that follows the numbered implementation specs and ADRs.

## Context

- Users should be able to install and run the app without using a terminal.
- Production packages must not show a terminal window.
- Development workflows may use debug scripts, but no terminal launcher is required.
- This file is an umbrella follow-up after the numbered specs, especially spec 017 and ADR 021.

## Scope

- Define production packaging outputs for Windows and Linux.
- Document dev setup separately from production installation.
- Separate core speech setup from optional dev-only keyboard mode.

## Out of scope

- App store packaging.

## Inputs

- Validated MVP.

## Outputs

- Windows installer (MSI or EXE) with no console window.
- Linux installer package (deb) or equivalent.
- Updated setup docs separating production installs from development workflows.

## Implementation requirements

- Follow ADR decision in `021-adr-packaging-toolchain.md`.
- Update `README.md` with:
	- Production installation section (Windows + Linux installers).
	- Dev setup section (virtualenv + developer runner script usage).
	- Explicit note that production runs without a terminal window.
	- Optional speech dependencies section tied to ADR 018.
	- Troubleshooting section for missing optional dependencies.
- Avoid documenting a terminal launcher.

Pseudo-code summary:

```text
pyinstaller --windowed --onefile src
```

## Acceptance criteria

- A fresh setup can install a production package without using a terminal.
- A dev setup can run a developer runner script without speech dependencies.

## Manual validation

- Clone into a clean environment and run setup instructions.

## Dependencies

- `016-manual-mvp-validation.md` - path: `.github/specs/016-manual-mvp-validation.md`
- `015-add-tests.md` - path: `.github/specs/015-add-tests.md`
- `017-package-local-runner.md` - path: `.github/specs/017-package-local-runner.md`
- `018-adr-offline-speech-engine-selection.md` - path: `.github/specs/018-adr-offline-speech-engine-selection.md`
- `021-adr-packaging-toolchain.md` - path: `.github/specs/021-adr-packaging-toolchain.md`

## Reference to Next step

Future specs may add hotword detection, macros, GUI, or online adapters.
