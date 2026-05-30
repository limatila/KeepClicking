# 021 - ADR: Packaging Toolchain Selection

Status: `[COMPLETE]`

## Purpose

Select the packaging toolchain for Windows and Linux production installers.

## Context

- Production packages must not show a terminal window.
- Windows users expect an installer (MSI or EXE) they can click to install.
- Linux users expect a deb package or equivalent.

## Scope

- Decide the packaging toolchain and output formats for MVP.
- Record implications for build scripts and documentation.

## Out of scope

- Implementing the packaging pipeline.
- App store submission.

## Inputs

- Toolchain comparison: output formats, maintenance cost, cross-platform support.

## Outputs

- Decision statement and consequences for specs.

## Implementation requirements

- Comparison summary:
  - PyInstaller: mature, supports onefile and windowed builds, common for Windows and Linux.
  - Nuitka: strong performance, longer build times, more complex setup.
  - Briefcase: app packaging focus, but more opinionated.
- Decision: Use PyInstaller for MVP packaging.
- Consequences:
  - Windows: build a windowed EXE (no console) and wrap with an installer (MSI or EXE) if needed.
  - Linux: build a binary and package into deb format.

## Acceptance criteria

- Decision is recorded with a clear rationale.
- MVP packaging spec references this ADR.

## Manual validation

- Review the decision with the user and mark status once approved.

## Dependencies

- None.

## Reference to Next step

`MVP-package-local-runner.md` - path: `.github/specs/MVP-package-local-runner.md`
