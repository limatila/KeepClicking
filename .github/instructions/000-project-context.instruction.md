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
- Whisper.cpp or faster-whisper
- Online speech-to-text providers

## MVP activation model

The MVP should start with push-to-talk or explicit CLI activation.

Always-on hotword detection is a future feature.
Always-on background daemon

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
