"""Application runner entry point."""

from __future__ import annotations

import logging
from typing import Callable

from src.commands.parser import CommandParser
from src.commands.validator import CommandValidator
from src.core.config import AppConfig
from src.core.errors import KeepClickingError, OptionalDependencyError
from src.service.mouse_controller import MouseController
from src.speech.interfaces import SpeechAdapter


class ApplicationRunner:
	"""Coordinates the speech-to-action pipeline execution loop."""

	def __init__(
		self,
		adapter: SpeechAdapter,
		normalizer: Callable[[str], str],
		parser: CommandParser,
		validator: CommandValidator,
		controller: MouseController,
		config: AppConfig,
		logger: logging.Logger,
	) -> None:
		self._adapter = adapter
		self._normalizer = normalizer
		self._parser = parser
		self._validator = validator
		self._controller = controller
		self._config = config
		self._logger = logger

	def run(self) -> None:
		try:
			self._logger.info("runner_started")
			while True:
				try:
					text = self._adapter.next_text()
					if text is None:
						self._logger.info("adapter_end")
						break
					if text == "":
						continue

					normalized = self._normalizer(text)
					self._logger.debug("normalized_text: %s", normalized)

					parse_result = self._parser.parse(normalized, self._config)
					if parse_result.command is None:
						if parse_result.error is not None:
							self._logger.warning(
								"parse_error: %s", parse_result.error.reason
							)
						continue

					validation = self._validator.validate(parse_result.command)
					if validation.command is None:
						if validation.error is not None:
							self._logger.warning(
								"validation_error: %s", validation.error.reason
							)
						continue

					execution = self._controller.execute(
						validation.command, self._config
					)
					if execution.error is not None:
						self._logger.error("execution_error: %s", execution.error)
					if execution.stopped:
						self._logger.info("execution_stopped")
						break
				except OptionalDependencyError as exc:
					self._logger.error("dependency_error: %s", exc)
					break
				except KeepClickingError as exc:
					self._logger.error("runtime_error: %s", exc)
					continue
		finally:
			self._adapter.close()
