# KeepClicking

KeepClicking is currently released as a CLI-only offline voice mouse controller for Windows-focused development. Packaging and installer flows are not documented yet.

## Installation

1. Install Python 3.11.
2. Install `uv`.
3. Clone this repository and enter the project root.
4. Install dependencies:

```powershell
uv sync
```

5. Optional: create a `.env` file in the repository root to override defaults.

```env
audio_input_device=USB 2.0
wake_word_listen_seconds=4.0
```

6. List the microphone names and microphone registry indexes KeepClicking can use:

```powershell
uv run python -m src.cli --list-audio-devices
```

7. Start the CLI:

```powershell
uv run python -m src.cli
```

Notes:

- `.env` keys for configuration are read from the repository root (`KeepClicking/.env`) and are expected in lowercase, exactly as shown in `src/core/config.py`.
- The default wake-word model already points to a bundled file: `src/resources/models/openwakeword/keeper_v1.onnx`.
- The default offline speech model already points to a bundled Vosk directory: `src/resources/models/vosk/vosk-model-small-en-us-0.15`.
- OpenWakeWord also needs its support models (`melspectrogram.onnx` and `embedding_model.onnx`). The runtime first looks for them in the installed `openwakeword` package and falls back to `.cache/openwakeword` if it needs to download them.

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

Commands that are currently implemented in the CLI:

- `click`
- `double click`
- `right click`
- `scroll up`
- `scroll down`
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
double click
```

```text
keeper
scroll down
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

- The wake word and the command are handled as a sequence. The runtime listens for the wake word first, then records the command phrase.
- The default command listening window is `5.0` seconds.
- `stop` ends the running CLI loop.
- `scroll` currently supports `up` and `down`.

## Possible Errors

These are the main errors you can hit in the current CLI flow:

- `Audio input device index '...' is not a valid available index`
  `audio_input_device` was set to an index that is not currently available/existent.
- `Audio input device '...' not found`
  `audio_input_device` did not match any available microphone name or alias.
- `No input-capable audio devices were found.`
  No usable microphone was returned by `sounddevice`.
- `parse_error: unrecognized_command`
  The recognized speech was outside the currently supported command set.
- `parse_error: missing_command_direction`
  The command was recognized as `move` or `scroll`, but no direction was detected.
- `validation_error: invalid_scroll_direction`
  `scroll` was recognized with a direction that is not currently supported.
- `Vosk adapter failure`
  A lower-level speech capture or Vosk runtime error happened.
- `OpenWakeWord model initialization failed`
  The wake-word model or its support assets could not be loaded correctly.
- `PyAutoGUI command failed`
  Mouse execution failed. PyAutoGUI fail-safe protection is enabled by default, so moving the cursor to a screen corner can stop automation.

## Configuration Options

This section is based on `src/core/config.py` and cross-checked against the tests. The live CLI behavior comes directly from `src/core/config.py`.

| `.env` key | Default | Consequence in the current CLI |
| --- | --- | --- |
| `debug_mode` | `False` | Keeps the CLI in normal runtime mode unless explicitly enabled. |
| `openwakeword_model_path` | `src/resources/models/openwakeword/keeper_v1.onnx` | Selects which OpenWakeWord model file is used to detect the activation word. |
| `offline_model_path` | `src/resources/models/vosk/vosk-model-small-en-us-0.15` | Selects the bundled Vosk model directory used for offline speech recognition. |
| `pyautogui_pause_seconds` | `0.1` | Adds a pause after PyAutoGUI actions. Higher values make actions safer/slower; lower values make them faster. |
| `pyautogui_failsafe` | `True` | Keeps PyAutoGUI fail-safe protection enabled unless explicitly disabled. |
| `mouse_movement_pixels` | `50` | Controls how far each `move <direction>` command moves the cursor. |
| `mouse_scroll_units` | `300` | Controls how far each `scroll up/down` command scrolls. |
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

## Windows Notes

- If `uv run ...` hits a local cache permission error on Windows, use the already-created virtual environment directly as a fallback:

```powershell
.\.venv\Scripts\python -m src.cli
```

- The project is not packaged as `.exe` yet. The current goal of this branch is to keep the CLI runtime stable and keep the dependencies and bundled models ready for that next step.
