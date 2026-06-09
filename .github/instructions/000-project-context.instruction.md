---
description: "This file provides the overall context for the KeepClicking project, including its purpose, core decisions, and non-goals. It serves as a reference for all implementation steps and specs."
name: "KeepClicking Project Context"
applyTo: "*"
---

# 000 — Project Context

## Project name

KeepClicking

## Purpose

KeepClicking is a local voice-controlled mouse automation system.

The user speaks a command. The application converts the speech into text, parses the command, validates the resulting action, and executes the mouse operation through PyAutoGUI.

## Core decision

PyAutoGUI is the final backend mouse executor.

## Preferred speech approach

Offline-first speech recognition is preferred because it avoids cost, rate limits, internet dependency, and privacy concerns.

The speech engine must remain adapter-based so the project can later support:

- Vosk
- faster-whisper
- Online speech-to-text providers

The current repository implementation uses OpenWakeWord for activation and Vosk for offline speech recognition.

## MVP activation model

The MVP must be speech-first with wake-word activation and offline speech recognition.

Always-on hotword detection with a short listen window after wake word.
Always-on background daemon is the intended production mode.

CLI usage is for development, debugging, and testing only.
Production packages must not show a terminal window to the user.
The current local entrypoint is `src/cli.py`, which wires the wake-word + offline speech pipeline directly.

GUI-based configuration is a nice-to-have for the future but is deferred for MVP simplicity.

## MVP user commands

- click
- double click
- right click
- scroll up
- scroll down
- move up
- move down
- move left
- move right
- stop

## Non-goals for MVP

- Macro scripting
