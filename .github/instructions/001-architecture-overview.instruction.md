---
description: "Architecture overview for KeepClicking, including the main layers and their responsibilities."
name: "KeepClicking Architecture Overview"
# applyTo: "src/**/*.py"
---

# 001 - Architecture Overview

## Technologies involved

- Python 3.11
- python-dotenv
- numpy
- SoundDevice
- OpenWakeWord
- Vosk (current offline engine)
- PyAutoGUI
- ONNX Runtime
- Pytest (dev only)
- PyInstaller (dev packaging tool only)

## Flow overview

```text
Microphone
    │
    ▼
Audio Capture
    │
    ▼
Wake Word Detection ("Hey Keeper") -> [3s Speech Listening Window]
    │
    ▼
Speech-to-Text
    │
    ▼
Text Normalizer
    │
    ▼
Command Parser (Translate normalized text to internal command objects)
    │
    ▼
Command Validator
    │
    ▼
Action Executor (mouse manager)
    │
    ▼
PyAutoGUI
    │
    ▼
Mouse Action Performed
```

## Folder Organization

```text
KeepClicking/
  src/
    __init__.py
    main.py                  production entrypoint
    cli.py                   dev-only harness
    core/
      config.py
      choices.py
      dataclasses.py
      errors.py
      logging.py
      interfaces/
    command_mapper/
      command_shapes.py
      dataclasses.py
      interfaces.py
      normalizer_dispatchers.py
      normalizers/
      parser.py
      validator.py
    speech/
      interfaces.py
      audio_device_resolver.py
      offline_adapters/
      wakeword/
    service/
      application_runner.py
      dataclasses.py
      hardware_controller.py
      interfaces.py
    resources/
      models/
        openwakeword/
        vosk/
  tests/
  docs/
  pyproject.toml
  requirements.txt
```

## Main architectural preferences

- Modularity: each layer has one responsibility and can be tested independently.
- Abstraction: higher layers depend on internal command objects and protocols, not PyAutoGUI.
- Testability: deterministic layers use unit tests and mocks; automated tests must not move the real mouse.

## Naming and base patterns

Use the pattern: "Implementation Goal BasePattern".

- Implementation: technology or strategy, such as Vosk, OpenWakeWord, or PyAutoGUI.
- Goal: domain capability, such as Speech, WakeWord, Mouse, or Command.
- BasePattern: reusable interface or abstract role, such as Adapter, Engine, Parser, Validator, or Controller.

Example: `VoskSpeechAdapter` means Vosk is the implementation, Speech is the goal, and Adapter is the base pattern.

Rules:

- Base patterns must be defined as Protocols, ABCs, or base classes.
- Concrete implementations should keep the implementation or domain role in the class name, such as `VoskSpeechAdapter`, `OpenWakeWordEngine`, `PyAutoGuiMouseController`, `MouseCommandParser`, `MouseCommandValidator`, and `MouseApplicationRunner`.
- Higher layers depend on base patterns, not concrete implementations.

## Project layers

### Core

Contains shared utilities, base classes, choices, dataclasses, errors, logging, and configuration.

### Speech Engine

Captures audio and returns recognized text. The current runtime uses OpenWakeWord for activation and Vosk for offline speech recognition.

### Text Normalizer

Normalizes recognized phrases to predictable canonical command strings.

### Command Parser

Converts normalized text into structured command objects.

### Command Validator

Rejects unsupported or unsafe command objects before execution.

### Mouse Controller

Executes validated mouse commands through PyAutoGUI.

### Application Runner

Wires all layers together for the speech-first pipeline.
`src/main.py` is the production entrypoint.
`src/cli.py` is a dev-only harness used for testing and debugging and is excluded from production packages.

## Architecture rule

Only the Mouse Controller may directly import and call PyAutoGUI.
In the current repository, that integration boundary is `src/service/hardware_controller.py`.

Other modules must depend on internal command objects, not PyAutoGUI.
