"""Mouse controller interfaces and implementations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import pyautogui

from src.core.config import AppConfig
from src.core.errors import MouseExecutionError
from src.core.models import Command, CommandAction, CommandDirection

LOGGER = logging.getLogger("baseLogger.mouse")


@dataclass(frozen=True)
class ExecutionResult:
	"""Represents the outcome of a mouse command execution."""

	stopped: bool
	error: str | None


class MouseController(Protocol):
	"""Base interface for mouse controllers."""

	def execute(self, command: Command, config: AppConfig) -> ExecutionResult:
		"""Execute a command and return the execution result."""


class PyAutoGuiMouseController:
	"""PyAutoGUI-backed mouse controller implementation."""

	def execute(self, command: Command, config: AppConfig) -> ExecutionResult:
		LOGGER.debug("mouse_execute: %s", command.action)
		pyautogui.PAUSE = config.pyautogui_pause_seconds
		pyautogui.FAILSAFE = config.pyautogui_failsafe

		try:
			if command.action == CommandAction.CLICK:
				pyautogui.click()
				return ExecutionResult(stopped=False, error=None)
			if command.action == CommandAction.DOUBLE_CLICK:
				pyautogui.doubleClick()
				return ExecutionResult(stopped=False, error=None)
			if command.action == CommandAction.RIGHT_CLICK:
				pyautogui.rightClick()
				return ExecutionResult(stopped=False, error=None)
			if command.action == CommandAction.SCROLL:
				if command.direction == CommandDirection.UP:
					pyautogui.scroll(command.amount)
					return ExecutionResult(stopped=False, error=None)
				if command.direction == CommandDirection.DOWN:
					pyautogui.scroll(-command.amount)
					return ExecutionResult(stopped=False, error=None)
			if command.action == CommandAction.MOVE:
				if command.direction == CommandDirection.UP:
					pyautogui.moveRel(0, -command.amount)
					return ExecutionResult(stopped=False, error=None)
				if command.direction == CommandDirection.DOWN:
					pyautogui.moveRel(0, command.amount)
					return ExecutionResult(stopped=False, error=None)
				if command.direction == CommandDirection.LEFT:
					pyautogui.moveRel(-command.amount, 0)
					return ExecutionResult(stopped=False, error=None)
				if command.direction == CommandDirection.RIGHT:
					pyautogui.moveRel(command.amount, 0)
					return ExecutionResult(stopped=False, error=None)
			if command.action == CommandAction.STOP:
				return ExecutionResult(stopped=True, error=None)
		except Exception as exc:  # pragma: no cover - integration guard
			LOGGER.error("mouse_error: %s", exc)
			raise MouseExecutionError("PyAutoGUI command failed") from exc

		raise MouseExecutionError("Unsupported or invalid command")
