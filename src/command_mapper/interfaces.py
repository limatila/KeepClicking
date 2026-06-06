from typing import Protocol

from src.core.config import AppConfig
from src.core.dataclasses import BaseCommand
from src.core.errors import ValidationError
from src.core.logging import VALIDATOR_LOGGER

from src.command_mapper.dataclasses import ParseResult, ValidationResult


class CommandValidator:
	"""Base interface for command validators."""
	def __init__(self):
		self.error = None
		self.command = None

	@property
	def validations_listing(self) -> list[callable]:
		"""
		Return a list of validation functions.
		Validation functions must always return a ValidationResult.
		"""
		
		raise NotImplementedError("validations_listing list must be implemented by subclasses")

	def validate(self, command: BaseCommand) -> ValidationResult:
		self.command = command

		for rule in self.validations_listing:
			try:
				rule()
			except ValidationError as err:
				self.error = err
				break
		
		if self.error:
			VALIDATOR_LOGGER.error("validation_failed: %s at %s", self.error.reason, self.error.field)
		else:
			VALIDATOR_LOGGER.debug("validation_ok: %s", command.action)
		
		return ValidationResult(command=self.command, error=self.error)


class CommandParser(Protocol):
	"""Base interface for command parsers."""

	def parse(self, text: str, config: AppConfig) -> ParseResult:
		"""Parse normalized text into a command or an error."""