# KeepClicking

KeepClicking is currently released as a CLI-only offline voice mouse controller. Packaging and installer flows are not documented yet.

## Installation

1. Install Python 3.11.
2. Install `uv`.
3. Clone this repository and enter the project root.
4. Install dependencies:

```powershell
uv sync
```

5. Create a `.env` file in the repository root with at least:

```env
offline_model_path=C:\path\to\your\vosk-model
```

6. list the microphone names and micrphone registry indexes KeepClicking can use:

```powershell
uv run python -m src.cli --list-audio-devices
```

7. Start the CLI:

```powershell
uv run python -m src.cli
```

Notes:

- `.env` keys for configuration are read from the repository root (`KeepClicking/.env`) and are currently expected in lowercase, exactly as shown in `src/core/config.py`.
- The default wake-word model path already points to a bundled file: `src/speech/wakeword/models/keeper_v1.onnx`. You can change it to use another file in that same folder

## How To Use

### CLI usage

- `uv run python -m src.cli`
  Starts the voice loop.
- `uv run python -m src.cli --list-audio-devices`
  Prints input-capable audio devices and exits.
- `uv run python -m src.cli -h`
  Shows the available CLI argument list.

### Speech usage in the CLI

The current voice flow is:

1. Start the CLI.
2. Say the activation word: `keeper`
3. After wake-word detection, say the command within the listening window.

Commands that are currently safe to treat as implemented in the CLI:

- `click`
- `move up`
- `move down`
- `move left`
- `move right`
- `stop`

Examples:

```text
keeper
click
```

```text
keeper
move right
```

```text
keeper
stop
```

Notes:

- The wake word and the command are handled as a sequence. The current runtime listens for the wake word first, then records the command phrase.
- The default command listening window is `5.0` seconds.
- `stop` ends the running CLI loop.
- `double click`, `right click`, and `scroll ...` appear in the codebase, but the current CLI parser/runtime path does not handle them reliably enough to document them as released commands yet.

## Possible Errors

These are the main errors you can hit in the current CLI flow:

- `Audio input device index '...' is not a valid available index`
  `audio_input_device` was set to an index that is not currently available/existant.
- `Audio input device '...' not found`
  `audio_input_device` did not match any available microphone name or alias.
- `No input-capable audio devices were found.`
  No usable microphone was returned by `sounddevice`.
- `parse_error: unrecognized_command`
  The recognized speech was outside the currently supported command set.
- `parse_error: missing_command_direction`
  The command was recognized as `move`, but no direction was detected.
- `Vosk adapter failure`
  A lower-level speech capture or Vosk runtime error happened.
- `OpenWakeWord model initialization failed`
  The wake-word model could not be loaded correctly.
- `PyAutoGUI command failed`
  Mouse execution failed. In the current CLI utility, PyAutoGUI fail-safe protection is enabled, possibiliting a application hault after the user moves the cursor to a screen corner.

## Configuration Options

This section is based on `src/core/config.py` and cross-checked against `tests/test_config.py`. When those differ, the live CLI behavior comes from `src/core/config.py` plus the explicit `debug_mode=True` override in `src.cli`.

| `.env` key | Default | Consequence in the current CLI |
| --- | --- | --- |
| `debug_mode` | `False` in `AppConfig`; forced to `True` by `src.cli` | Enables debug-oriented runtime behavior in the CLI. Because the CLI forces this on, logs are more verbose and PyAutoGUI fail-safe is auto-enabled when unset. |
| `openwakeword_model_path` | `src/speech/wakeword/models/keeper_v1.onnx` | Selects which OpenWakeWord model file is used to detect the activation word. If you change this, detection behavior follows the new model. |
| `pyautogui_pause_seconds` | `0.1` | Adds a pause after PyAutoGUI actions. Higher values make actions safer/slower; lower values make them faster. |
| `pyautogui_failsafe` | unset by default | When unset and debug mode is on, it becomes enabled automatically. With fail-safe enabled, moving the cursor into a fail-safe corner can abort mouse automation. |
| `mouse_movement_pixels` | `50` | Controls how far each `move <direction>` command moves the cursor. |
| `mouse_scroll_units` | `300` | Intended to control scroll distance, but the current released CLI command set does not expose scrolling reliably yet. |
| `keyboard_prompt` | `keepclicking> ` | Present in config, but not used by the current voice CLI path. |
| `offline_model_path` | `None` | Required for the Vosk speech recognizer. This must point to a valid local Vosk model directory or the voice CLI will fail after wake-word detection. |
| `wake_word_phrase` | `keeper` | Changes the expected activation phrase in logs/config. In practice, wake-word detection still depends on the model selected by `openwakeword_model_path`, so these two settings should stay aligned. |
| `wake_word_listen_seconds` | `5.0` | Controls how long the CLI records audio after wake-word detection. Shorter values may cut commands off; longer values capture more silence before transcription completes. |
| `audio_input_device` | `None` | Chooses the microphone. Leave unset to use the system default input device. You can also set a numeric index or a fuzzy device name such as `USB 2.0`. |

## Audio Device Selection

`audio_input_device` currently supports:

- `None` or empty/not present: use the system default input device
- A numeric device index such as `1`
- A device name or partial name such as `USB 2.0`
- Normalized matches such as `USB2.0`
- On ALSA-based systems, certain card aliases as well

If you are unsure which devices are available to use, run:

```powershell
uv run python -m src.cli --list-audio-devices
```
