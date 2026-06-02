"""Logging configuration utilities."""

from __future__ import annotations

import logging
from logging import DEBUG, INFO

from src.core.config import get_env_or_default

DEFAULT_LOG_FORMAT = get_env_or_default("LOGGING_FORMAT", "[%(levelname)s] | %(name)s -|- %(message)s")


CORE_LOGGER = logging.getLogger('baseLogger.core')
RUNNER_LOGGER = logging.getLogger('baseLogger.runner')
PARSER_LOGGER = logging.getLogger('baseLogger.parser')
VALIDATOR_LOGGER = logging.getLogger('baseLogger.validator')
CONTROLLER_LOGGER = logging.getLogger('baseLogger.controller')


for logger in [CORE_LOGGER, RUNNER_LOGGER, PARSER_LOGGER, VALIDATOR_LOGGER, CONTROLLER_LOGGER]:
	
	if not logger.handlers:
		handler = logging.StreamHandler()
		formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

		if logger.name == "baseLogger.core":
			handler.setLevel(DEBUG)
		else:
			handler.setLevel(INFO)

		handler.setFormatter(formatter)
		logger.addHandler(handler)

	if logger.name == "baseLogger.core":
		logger.propagate = False


CORE_LOGGER.info("loggers initialized")
