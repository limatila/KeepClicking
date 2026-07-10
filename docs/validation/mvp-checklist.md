# MVP Validation Checklist

## Environment

- OS: Windows
- Python version:
- Execution path: `uv run python -m src.cli` / `.\.venv\Scripts\python -m src.cli`

## Input Mode

- Mode: speech_offline
- Wake word model:
- Offline speech model:
- Audio input device:

## CLI Smoke Tests

- `python -m src.cli -h`: pass/fail
- `python -m src.cli --list-audio-devices`: pass/fail
- CLI boot without mandatory `.env`: pass/fail

## Speech (Offline) Validation

- click: pass/fail
- double click: pass/fail
- right click: pass/fail
- scroll up: pass/fail
- scroll down: pass/fail
- move up: pass/fail
- move down: pass/fail
- move left: pass/fail
- move right: pass/fail
- stop: pass/fail

## Windows Runtime Notes

- OpenWakeWord support assets resolved from installed package: pass/fail
- OpenWakeWord support assets resolved from `.cache/openwakeword`: pass/fail
- Vosk bundled model loaded: pass/fail
- PyAutoGUI fail-safe behaved as expected: pass/fail

## Notes / Issues

-
