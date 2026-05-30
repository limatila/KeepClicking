# KeepClicking

KeepClicking is an offline-first, voice-controlled mouse automation tool focused on accessibility and long-running stability.

## Production Installation

### Linux (MVP target)

- Install the Linux package (.deb) from the releases page using your system package manager.
- Launch KeepClicking from your desktop menu. Production runs without a terminal window.

### Windows (Planned)

- Install the Windows installer (.exe or .msi) from the releases page.
- Launch KeepClicking from the Start menu. Production runs without a terminal window.

## Dev Setup (Contributors)

- Create a virtual environment for Python 3.13+.
- Install dependencies for development.
- Use the developer runner script (see src/cli.py) with the keyboard adapter for quick debugging.

The keyboard adapter is dev-only and is not intended for production packages.

## Optional Speech Dependencies (Offline)

Offline speech uses Vosk with OpenWakeWord for wake-word detection. These dependencies are optional if you only use the dev keyboard adapter.

- Vosk model files must be provided via the configured offline model path.
- OpenWakeWord and SoundDevice are required for wake-word detection and microphone capture.

## Troubleshooting

- Missing optional speech dependencies: use the dev keyboard adapter or install the missing packages.
- Wake word not detected: confirm the OpenWakeWord model and microphone permissions are working.
