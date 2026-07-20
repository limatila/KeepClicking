# MVP Validation Checklist

## Validation Record

- Date: 2026-07-20
- OS: Windows 10.0.19045
- Python version: 3.11.15
- Automated test command: `uv run pytest`
- Automated test result: pass, 86 passed
- Production entrypoint smoke: pass
- Packaged executable: `dist/KeepClicking.exe`
- Packaged executable size: 127,547,748 bytes
- Packaged executable smoke: pass by exit code for `-h` and `--list-audio-devices`
- Packaged archive exclusion check: pass for project/dev paths, old wake-word models, PT Vosk model, and sklearn dataset test data
- Live speech/manual mouse validation: not run in this agent session; requires a human desktop pass with microphone and safe mouse target

## Input Mode

- Production mode: `src/main.py`
- Dev harness: `src/cli.py`
- Speech mode: offline Vosk gated by OpenWakeWord
- Wake word model: `src/resources/models/openwakeword/hey_keeper_v2.onnx`
- OpenWakeWord support assets:
  - `src/resources/models/openwakeword/melspectrogram.onnx`
  - `src/resources/models/openwakeword/embedding_model.onnx`
- Offline speech model: `src/resources/models/vosk/vosk-model-small-en-us-0.15`
- Audio input device: system default when `audio_input_device` is unset

## Smoke Tests

- `uv run python -m src.main -h`: pass
- `uv run python -m src.main --list-audio-devices`: pass
- `dist/KeepClicking.exe -h`: pass by exit code
- `dist/KeepClicking.exe --list-audio-devices`: pass by exit code
- CLI boot without mandatory `.env`: covered by automated tests

## Command Validation

| Command | Automated command path | Live speech/manual mouse |
| --- | --- | --- |
| `click` | pass | not run |
| `double click` | pass | not run |
| `right click` | pass | not run |
| `scroll up` | pass | not run |
| `scroll down` | pass | not run |
| `move up` | pass | not run |
| `move down` | pass | not run |
| `move left` | pass | not run |
| `move right` | pass | not run |
| `stop` | pass | not run |

## Windows Runtime Notes

- OpenWakeWord support assets bundled under production resources: pass
- Production packaging avoids `.cache/openwakeword` as a required runtime source: pass
- Vosk bundled model present: pass
- `audio_input_device=None` uses the system default SoundDevice input: pass
- PyAutoGUI fail-safe remains enabled by default: pass

## Notes / Issues

- Live speech validation still needs a human run in a safe desktop environment.
- The windowed EXE intentionally does not expose console output during packaged smoke checks; exit code was used for validation.
