---
description: "This file defines the command contract for the KeepClicking application, specifying the structured format for parsed commands and the supported actions. It serves as a reference for the Command Parser and Mouse Controller implementation steps."
name: "Command Contracts"
# applyTo: "src/*"
---

# 002 — Command Contract

## Command object

Every parsed command must be represented as a structured object.
In the current repository this is `MouseCommand` from `src/core/dataclasses.py`, using enums from `src/core/choices.py`.

Minimum fields:

```python
{
    "action": "click",
    "amount": 1,
    "direction": None
}
```

## Supported actions

| Action | Direction | Amount | Meaning |
| --- | --- | --- | --- |
| click | null | 1 | single left click |
| double_click | null | 2 | double left click |
| right_click | null | 1 | right click |
| scroll | up | configurable | scroll up |
| scroll | down | configurable | scroll down |
| move | up | configurable | move cursor up |
| move | down | configurable | move cursor down |
| move | left | configurable | move cursor left |
| move | right | configurable | move cursor right |
| stop | null | 0 | stop current command loop |

Structured action values stay in enum format such as `double_click` and `right_click`.
Choices define the available action and direction primitives, and the shared command-shape registry defines which combinations are valid.
The canonical spoken command catalog is resolved in `src/command_mapper/normalizers/mappings.py` from those choices plus the shared shape rules and currently contains:

- `stop`
- `click`
- `double click`
- `right click`
- `scroll up`
- `scroll down`
- `move up`
- `move down`
- `move left`
- `move right`

## Parser examples

| Input text | Command |
| --- | --- |
| click | click |
| clique | click |
| double click | double_click |
| right click | right_click |
| scroll up | scroll up |
| scroll down | scroll down |
| move left | move left |
| move right | move right |
| stop | stop |

## Rule

The parser must not execute commands.

The mouse controller must not interpret raw text.

Current implementation note:
`MouseCommand` resolves default amounts from configuration at construction time. Choices only resolve their own enum from text, while parser, validator, and canonical command generation all consult the shared command-shape registry for structure rules.
