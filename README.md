# KeepClicking

KeepClicking is currently released as a CLI-only offline voice mouse controller for Windows-focused usage. Packaging and installer flows are not documented yet.

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
- The default wake-word model already points to a bundled file: `src/resources/models/openwakeword/hey_keeper_v2.onnx`.
- The default offline speech model is selected from `speech_language`: `en_us` uses `src/resources/models/vosk/vosk-model-small-en-us-0.15`, and `pt_br` uses `src/resources/models/vosk/vosk-model-small-pt-0.3`.
- OpenWakeWord also needs its support models (`melspectrogram.onnx` and `embedding_model.onnx`). The runtime first looks for them in the installed `openwakeword` package and falls back to `.cache/openwakeword` if it needs to download them.

## Packaging

Windows builds are produced from `src/main.py` as separate EXEs, one per bundled offline speech model:

- `dist/KeepClicking-en-us.exe`
- `dist/KeepClicking-pt-br.exe`

Build them with:

```powershell
.\scripts\build_exe.ps1
```

Or one variant at a time:

```powershell
.\scripts\build_exe.ps1 -Variant en-us
.\scripts\build_exe.ps1 -Variant pt-br
```

Each EXE bundles only its matching Vosk model for size reduction. If a local `.env` override points `offline_model_path` at a model directory that is not present in that package, startup fails with a clear Vosk adapter error.

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
2. Say the activation word: `hey keeper`
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
hey keeper
click
```

```text
hey keeper
double click
```

```text
hey keeper
scroll down
```

```text
hey keeper
move right
```

```text
hey keeper
stop
```

Notes:

- The wake word and the command are handled as a sequence. The runtime listens for the wake word first, then records the command phrase.
- The default command listening window is `3.0` seconds.
- `stop` ends the running CLI loop.
- `scroll` currently supports `up` and `down`, and bare `scroll` is treated as incomplete input rather than a canonical command.
- Speech normalization supports both `en_us` and `pt_br`, while still feeding the parser with canonical English commands.
- `speech_language` also selects the default bundled Vosk model unless `offline_model_path` is explicitly overridden.

## Possible Errors

These are the main errors you can hit in the current CLI flow:

- `Audio input device index '...' is not a valid available index`
  `audio_input_device` was set to an index that is not currently available/existent.
- `Audio input device '...' not found`
  `audio_input_device` did not match any available microphone name or alias.
- `No input-capable audio devices were found.`
  No usable microphone was returned by `sounddevice`.
- `parse_error: unrecognized_command`
  The normalized speech was outside the currently supported canonical command set.
- `parse_error: missing_command_direction`
  The normalized command was recognized as `move` or `scroll`, but no direction was detected.
- `validation_error: invalid_scroll_direction`
  `scroll` was recognized with a direction that is not currently supported.
- `speech_normalization_failure`
  A structural failure happened inside the speech normalizer layer.
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
| `speech_language` | `en_us` | Selects the speech normalizer and the default bundled Vosk model. Current supported values are `en_us` and `pt_br`. |
| `openwakeword_model_path` | `src/resources/models/openwakeword/hey_keeper_v2.onnx` | Selects which OpenWakeWord model file is used to detect the activation word. |
| `offline_model_path` | language-specific default | Selects the Vosk model directory used for offline speech recognition. If unset, it follows `speech_language`. |
| `pyautogui_pause_seconds` | `0.1` | Adds a pause after PyAutoGUI actions. Higher values make actions safer/slower; lower values make them faster. |
| `pyautogui_failsafe` | `True` | Keeps PyAutoGUI fail-safe protection enabled unless explicitly disabled. |
| `mouse_movement_pixels` | `200` | Controls how far each `move <direction>` command moves the cursor. |
| `mouse_scroll_units` | `350` | Controls how far each `scroll up/down` command scrolls. |
| `wake_word_phrase` | `hey keeper` | Changes the expected activation phrase in logs/config. In practice, wake-word detection still depends on the model selected by `openwakeword_model_path`, so these two settings should stay aligned. |
| `wake_word_listen_seconds` | `3.0` | Controls how long the CLI records audio after wake-word detection. Shorter values may cut commands off; longer values capture more silence before transcription completes. |
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

- Production packaging is supported through `.\scripts\build_exe.ps1`, which produces `KeepClicking-en-us.exe` and `KeepClicking-pt-br.exe`.
