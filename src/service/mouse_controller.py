"""Mouse controller interfaces and implementations."""

from __future__ import annotations

import logging

import pyautogui as pag

from src.core.dataclasses import MouseCommand
from src.core.config import AppConfig
from src.core.errors import MouseExecutionError
from src.core.choices import MouseCommandAction, CommandDirection

from src.service.dataclasses import MouseExecutionResult
from src.service.interfaces import Controller

LOGGER = logging.getLogger("baseLogger.mouse")


class PyAutoGuiMouseController(Controller):
	"""PyAutoGUI-backed mouse controller implementation."""
	def __init__(self):
		self.stopped = False
		self.error = None

	def click(self, times: int = 1, right_click: bool = False):
		for _ in range(times):
			if right_click:
				pag.rightClick()
			else:
				pag.click()

	def scroll(self, command: MouseCommandAction):
		if command.direction == CommandDirection.UP:
			pag.scroll(command.amount)
		if command.direction == CommandDirection.DOWN:
			pag.scroll(-command.amount)

	def move_cursor(self, command: MouseCommandAction):
		if command.direction == CommandDirection.UP:
			pag.moveRel(0, -command.amount)
		
		if command.direction == CommandDirection.DOWN:
			pag.moveRel(0, command.amount)
		
		if command.direction == CommandDirection.LEFT:
			pag.moveRel(-command.amount, 0)
		
		if command.direction == CommandDirection.RIGHT:
			pag.moveRel(command.amount, 0)

	def execute(self, command: MouseCommand, config: AppConfig) -> MouseExecutionResult:
		pag.PAUSE = config.pyautogui_pause_seconds
		pag.FAILSAFE = config.pyautogui_failsafe

		def _dispatch_command(command: MouseCommand):
			command_dispatcher: dict[MouseCommandAction, callable] = {
				MouseCommandAction.CLICK: lambda: self.click(),
				MouseCommandAction.DOUBLE_CLICK: lambda: self.click(times=2),
				MouseCommandAction.RIGHT_CLICK: lambda: self.click(times=command.amount, right_click=True),
				MouseCommandAction.SCROLL: lambda: self.scroll(command),
				MouseCommandAction.MOVE: lambda: self.move_cursor(command)
			}

			command = command_dispatcher.get(command.action)

			if command:
				command()
			
			return True if command else False

		
		try:
			if command.action == MouseCommandAction.STOP:
				self.stopped = True
			
			else:
				has_executed = _dispatch_command(command)
				
				if not has_executed:
					self.error = MouseExecutionError("Unsupported or invalid command")
				else:
					LOGGER.debug("mouse_execute: %s", command.action)
			
			return MouseExecutionResult(stopped=self.stopped, error=self.error)

		except Exception as err:
			LOGGER.error("mouse_error: %s", err)
			raise MouseExecutionError("PyAutoGUI command failed") from err
