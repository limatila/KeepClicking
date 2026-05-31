from src.core.config import AppConfig
from src.core.dataclasses import MouseCommand
from src.service.dataclasses import MouseExecutionResult


from typing import Protocol


class Controller(Protocol):
	"""Base interface for mouse controllers."""

	def execute(self, command: MouseCommand, config: AppConfig) -> MouseExecutionResult:
		"""Execute a command and return the execution result."""