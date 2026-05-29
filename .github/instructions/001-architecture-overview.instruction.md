---
description: "This files provide a overview of the architecture of the KeepClicking application, including its main layers and their responsibilities. It serves as a reference for all implementation steps and specs."
name: "KeepClicking Architecture Overview"
# applyTo: "src/**/*.py"
---


# 001 — Architecture Overview

## Technologies involved

- Python 3.13+
│
├── SoundDevice
├── OpenWakeWord
├── Vosk (primary offline engine)
├── Faster-Whisper (optional alternative)
├── PyAutoGUI
├── PySide6 (deferred)
└── Pytest

## Flow overview

```text
Microphone
    │
    ▼
Audio Capture
    │
    ▼
Wake Word Detection ("Keeper") -> [5s Speech Listening Window]
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
│
├── src/
│   │
│   ├── __init__.py
│   ├── cli.py (dev-only harness)
│   ├── core/
│   │   ├── config.py
│   │   ├── errors.py
│   │   └── models.py
│   ├── audio/
│   │   └── capture.py
│   ├── wakeword/
│   │   └── detector.py
│   ├── speech/
│   │   ├── interfaces.py
│   │   └── offline_adapter.py
│   ├── commands/
│   │   ├── normalizer.py
│   │   ├── parser.py
│   │   └── validator.py
│   ├── service/
│   │   ├── mouse_controller.py
│   │   └── runner.py
│   └── utils/
│       └── logging.py
│
├── tests/
│   ├── test_audio.py
│   ├── test_wakeword.py
│   ├── test_speech.py
│   └── etc...
│
├── scripts/
│   ├── build.py
│   ├── package.py
│   └── release.py
│
├── requirements.txt
├── .python-version
└── pyproject.toml
```

## Main architectural preferences

- **Modularity**: Each layer has a single responsibility and can be developed and tested independently.
- **Abstraction**: Higher layers depend on abstract command objects, not on PyAutoGUI or implementation details.
- **Testability**: Each layer can be unit tested with mock inputs and outputs, without side effects or external dependencies.

Everything should be scalable and flexible enough for future additions

### Typed Payloads Usage

Dataclasses can be used as: **DTO (Data Transfer Objects)**: To represent structured command objects that flow between layers.
Strictly type of commands, standard strings, and choice-like data shall be as Enums (Enum, str):

```python
class BaseChoice(str, Enum): #* Defined at core of project for reuse
    pass

class CommandActionChoice(BaseChoice):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    MOVE = "move"
    STOP = "stop"
```

so then, they can be used as a type of attribute in a dataclass:

```python
@dataclass
class Command:
    action: CommandActionChoice
    amount: int
    direction: Optional[str] = None
```

## Project layers

### Core

Contains shared utilities, base classes, and common definitions used across the application.
Every layer you catch having a 'Base' behavior shall be moved to here, at core. or core.basic for more basic ones (not integration implementation, by instance).

### Speech Engine

Captures or receives audio and returns recognized text.

### Text Normalizer

Normalizes recognized phrases to predictable lowercase command strings.

### Command Parser

Converts normalized text into structured command objects.

### Command Validator

Rejects unsupported or unsafe command objects.

### Mouse Controller

Executes validated mouse commands through PyAutoGUI.

### Application Runner

Wires all layers together for the speech-first pipeline.
CLI is a dev-only harness used for testing and debugging.

## Architecture rule

Only the Mouse Controller may directly import and call PyAutoGUI.

Other modules must depend on internal command objects, not PyAutoGUI.
