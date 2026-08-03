# MVP Validation Checklist

## Validation Record

- Date: 2026-07-26
- OS: Windows 10.0.19045
- Python version: 3.11.15
- Automated test command: `uv run pytest`
- Automated test result: pass, 89 passed
- Production entrypoint smoke: pass
- Packaged executables:
  - `dist/KeepClicking-en-us.exe`
  - `dist/KeepClicking-pt-br.exe`
- Packaged executable smoke: pass by exit code for `-h` and `--list-audio-devices` on both language variants
- Packaged archive exclusion check: pass for project/dev paths, unused language models, and sklearn dataset test data
- Packaged startup/logging check: pass; `run_N.log` files were created during packaged smokes
- Live speech/manual mouse validation: not run in this agent session; requires a human desktop pass with microphone and safe mouse target

## Input Mode

- Production mode: `src/main.py`
- Dev harness: `src/cli.py`
- Speech mode: offline Vosk gated by OpenWakeWord
- Wake word model: `src/resources/models/openwakeword/hey_keeper_v2.onnx`
- OpenWakeWord support assets:
  - `src/resources/models/openwakeword/melspectrogram.onnx`
  - `src/resources/models/openwakeword/embedding_model.onnx`
- Offline speech models:
  - `en-us`: `src/resources/models/vosk/vosk-model-small-en-us-0.15`
  - `pt-br`: `src/resources/models/vosk/vosk-model-small-pt-0.3`
- Audio input device: system default when `audio_input_device` is unset
- Production logs: per-run `run_N.log` files under `~/Documents/keepclicking_logs`, with fallback to another writable user/temp path when `Documents` is unavailable
- Packaged config override support: `.env` and `<exe-name>.env` beside the EXE override bundled `packaged.env`

## Smoke Tests

- `uv run python -m src.main -h`: pass
- `uv run python -m src.main --list-audio-devices`: pass
- `dist/KeepClicking-en-us.exe -h`: pass by exit code
- `dist/KeepClicking-en-us.exe --list-audio-devices`: pass by exit code
- `dist/KeepClicking-pt-br.exe -h`: pass by exit code
- `dist/KeepClicking-pt-br.exe --list-audio-devices`: pass by exit code
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
- Vosk package DLLs collected into packaged `vosk` module: pass
- Vosk bundled model present: pass for both language variants, each with only its matching language model
- `audio_input_device=None` uses the system default SoundDevice input: pass
- PyAutoGUI fail-safe remains enabled by default: pass

## Notes / Issues

- Live speech validation still needs a human run in a safe desktop environment.
- The windowed EXE intentionally does not expose console output during packaged smoke checks; exit code is the expected smoke-check signal.
- On this Windows machine, `~/Documents` did not exist, so packaged logging fell back to `%TEMP%\\KeepClicking\\keepclicking_logs` and still produced `run_1.log` through `run_4.log`.
