"""Mouse controller interfaces and implementations."""

from __future__ import annotations

import pyautogui as pag

from src.core.dataclasses import MouseCommand
from src.core.config import AppConfig
from src.core.errors import MouseExecutionError
from src.core.choices import MouseCommandAction, CommandDirection
from src.core.logging import CONTROLLER_LOGGER

from src.service.dataclasses import MouseExecutionResult
from src.service.interfaces import Controller


class PyAutoGuiMouseController(Controller):
    """PyAutoGUI-backed mouse controller implementation."""
    def __init__(self):
        self.stopped = False
        self.error = None

    def click(self, times: int = 1, right_click: bool = False):
        button_side = "right" if right_click else "primary"
        pag.click(clicks=times, interval=0.05, button=button_side)

    def scroll(self, command: MouseCommand):
        if command.direction == CommandDirection.UP:
            pag.scroll(command.amount)
        if command.direction == CommandDirection.DOWN:
            pag.scroll(-command.amount)
        # TODO: add horizontal scrolling, x and y args

    def move_cursor(self, command: MouseCommand):
        if command.direction == CommandDirection.UP:
            pag.moveRel(0, -command.amount, duration=0.2)
        
        if command.direction == CommandDirection.DOWN:
            pag.moveRel(0, command.amount, duration=0.2)
        
        if command.direction == CommandDirection.LEFT:
            pag.moveRel(-command.amount, 0, duration=0.2)
        
        if command.direction == CommandDirection.RIGHT:
            pag.moveRel(command.amount, 0, duration=0.2)

    def execute(self, command: MouseCommand, config: AppConfig) -> MouseExecutionResult:
        self.stopped = False
        self.error = None

        pag.PAUSE = config.pyautogui_pause_seconds
        pag.FAILSAFE = config.pyautogui_failsafe

        def _dispatch_command(command: MouseCommand):
            command_executer_dispatcher: dict[MouseCommandAction, callable] = {
                MouseCommandAction.CLICK: lambda: self.click(times=command.amount),
                MouseCommandAction.DOUBLE_CLICK: lambda: self.click(times=command.amount),
                MouseCommandAction.RIGHT_CLICK: lambda: self.click(times=command.amount, right_click=True),
                MouseCommandAction.SCROLL: lambda: self.scroll(command),
                MouseCommandAction.MOVE: lambda: self.move_cursor(command)
            }

            hardware_executer = command_executer_dispatcher.get(command.action)

            if hardware_executer:
                hardware_executer()
            
            return True if hardware_executer else False

        try:
            if command.action == MouseCommandAction.STOP:
                self.stopped = True
                CONTROLLER_LOGGER.debug("user_stopped_command")
            
            else:
                has_executed = _dispatch_command(command)
                
                if not has_executed:
                    self.error = MouseExecutionError("Unsupported or invalid command")
                else:
                    CONTROLLER_LOGGER.debug("mouse_execute: %s", command.action)
            
            return MouseExecutionResult(stopped=self.stopped, error=self.error)

        except Exception as err:
            CONTROLLER_LOGGER.error("mouse_error: %s", err)
            raise MouseExecutionError("PyAutoGUI command failed") from err
