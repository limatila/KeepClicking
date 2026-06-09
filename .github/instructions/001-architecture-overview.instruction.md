---
description: "This files provide a overview of the architecture of the KeepClicking application, including its main layers and their responsibilities. It serves as a reference for all implementation steps and specs."
name: "KeepClicking Architecture Overview"
# applyTo: "src/**/*.py"
---


# 001 — Architecture Overview

## Technologies involved

- Python 3.11
│
├── python-dotenv
├── numpy
├── SoundDevice
├── OpenWakeWord
├── Vosk (current offline engine)
├── faster-whisper (installed for future evaluation, not wired into the current runtime path)
├── PyAutoGUI
├── ONNX Runtime
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
│   │   ├── choices.py
│   │   ├── dataclasses.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   └── interfaces/
│   │       └── choices.py
│   ├── command_mapper/
│   │   ├── dataclasses.py
│   │   ├── interfaces.py
│   │   ├── normalizer.py
│   │   ├── parser.py
│   │   └── validator.py
│   ├── speech/
│   │   ├── interfaces.py
│   │   ├── keyboard_adapter.py
│   │   ├── offline_vosk_adapter.py
│   │   └── wakeword/
|   |       ├── models/
│   │       └── engine.py
│   └── service/
│       ├── application_runner.py
│       ├── dataclasses.py
│       ├── hardware_controller.py
│       └── interfaces.py
│
├── tests/
│   ├── test_audio_device_resolver.py
│   ├── test_config.py
│   ├── test_mouse_controller.py
│   ├── test_normalizer.py
│   ├── test_offline_vosk_adapter.py
│   ├── test_parser.py
│   ├── test_runner.py
│   ├── test_validator.py
│   └── test_wakeword_engine.py
│
├── scripts/
│   └── build-global.py
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

## Naming and base patterns

Use the pattern: "Implementation Goal BasePattern".

- Implementation: technology or strategy (Vosk, OpenWakeWord, PyAutoGUI).
- Goal: domain capability (Speech, WakeWord, Mouse, Command).
- BasePattern: reusable interface or abstract role (Adapter, Engine, Parser, Validator, Controller).

Example sentence: "Vosk Speech Adapter" means Vosk is the implementation, Speech is the goal, Adapter is the base pattern.

Rules:

- Base patterns must be defined as Protocols/ABCs or base classes.
- Concrete implementations should keep the implementation or domain role in the class name (for example, `VoskSpeechAdapter`, `OpenWakeWordEngine`, `PyAutoGuiMouseController`, `MouseCommandParser`, `MouseCommandValidator`, `MouseApplicationRunner`).
- Higher layers depend on base patterns, not concrete implementations.

### Typed Payloads Usage

Dataclasses can be used as: **DTO (Data Transfer Objects)**: To represent structured command objects that flow between layers.
Strictly type of commands, standard strings, and choice-like data shall be as Enums (Enum, str):

```python
class BaseChoice(str, Enum): #* Defined at core of project for reuse
    pass

class MouseCommandAction(BaseChoice):
    STOP = "stop"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    MOVE = "move"
```

so then, they can be used as a type of attribute in a dataclass:

```python
@dataclass
class MouseCommand:
    action: MouseCommandAction
    amount: int
    direction: Optional[CommandDirection] = None
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
In the current repository, that integration boundary is `src/service/hardware_controller.py`.

Other modules must depend on internal command objects, not PyAutoGUI.
