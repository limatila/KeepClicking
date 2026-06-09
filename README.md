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

- Create a virtual environment for Python 3.11.
- Install dependencies for development.
- Use the developer runner entrypoint in `src/cli.py` for the current wake-word + offline speech path.
- Use `KeyboardSpeechAdapter` only for targeted local debugging or tests; it is available in `src/speech/keyboard_adapter.py` but is not the default CLI wiring.

The keyboard adapter is dev-only and is not intended for production packages.

## Optional Speech Dependencies (Offline)

Offline speech uses Vosk with OpenWakeWord for wake-word detection. These dependencies are required for the current CLI runner and optional only if you build your own keyboard-adapter-based dev harness.

- Vosk model files must be provided via the configured offline model path.
- OpenWakeWord and SoundDevice are required for wake-word detection and microphone capture.

## Troubleshooting

- Missing optional speech dependencies: use the dev keyboard adapter or install the missing packages.
- Wake word not detected: confirm the OpenWakeWord model and microphone permissions are working.
- Inspect the exact microphone names KeepClicking sees with `./.venv/bin/python -m src.cli --list-audio-devices`.
- `audio_input_device` accepts either a numeric index or a fuzzy device name. On Linux, values like `USB2.0` and `USB 2.0` are treated as the same selector.
