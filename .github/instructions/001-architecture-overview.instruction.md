---
description: "This files provide a overview of the architecture of the KeepClicking application, including its main layers and their responsibilities. It serves as a reference for all implementation steps and specs."
name: "KeepClicking Architecture Overview"
# applyTo: "src/**/*.py"
---


# 001 — Architecture Overview

Status: `[COMPLETE]`

## Pipeline

```text
Audio Input
  -> Speech Engine Adapter
  -> Text Normalizer
  -> Command Parser
  -> Command Validator
  -> Mouse Controller
  -> PyAutoGUI
```

## Main architectural preferences

- **Modularity**: Each layer has a single responsibility and can be developed and tested independently.
- **Abstraction**: Higher layers depend on abstract command objects, not on PyAutoGUI or implementation details.
- **Testability**: Each layer can be unit tested with mock inputs and outputs, without side effects or external dependencies.

Everything should be scalable and flexible enough for future additions

### Dataclasses Usage

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

Wires all layers together and exposes a CLI execution path.

## Architecture rule

Only the Mouse Controller may directly import and call PyAutoGUI.

Other modules must depend on internal command objects, not PyAutoGUI.
