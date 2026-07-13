"""Logging configuration utilities."""

from __future__ import annotations

import logging
from logging import DEBUG, INFO

from src.core.config import AppConfig, get_env_or_default

DEFAULT_LOG_FORMAT = get_env_or_default(
    "LOGGING_FORMAT",
    "[%(levelname)s] | %(name)s -|- %(message)s",
)
DEFAULT_HANDLER_NAME = "keepclicking_stream_handler"


CORE_LOGGER = logging.getLogger("baseLogger.core")
ADAPTER_LOGGER = logging.getLogger("baseLogger.adapter")
RUNNER_LOGGER = logging.getLogger("baseLogger.runner")
PARSER_LOGGER = logging.getLogger("baseLogger.parser")
VALIDATOR_LOGGER = logging.getLogger("baseLogger.validator")
CONTROLLER_LOGGER = logging.getLogger("baseLogger.controller")

ALL_LOGGERS = (
    CORE_LOGGER,
    ADAPTER_LOGGER,
    RUNNER_LOGGER,
    PARSER_LOGGER,
    VALIDATOR_LOGGER,
    CONTROLLER_LOGGER,
)




def configure_logging(config: AppConfig) -> None:
    
    def _get_or_add_default_handler(logger: logging.Logger) -> logging.Handler:
        for handler in logger.handlers:
            if getattr(handler, "name", "") == DEFAULT_HANDLER_NAME:
                return handler

        handler = logging.StreamHandler()
        handler.name = DEFAULT_HANDLER_NAME
        logger.addHandler(handler)
        return handler
    """Configure package loggers using the effective runtime config."""

    log_level = DEBUG if config.debug_mode else INFO
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    for logger in ALL_LOGGERS:
        logger.setLevel(log_level)
        
        if logger.name == "baseLogger.core":
            logger.propagate = False

        setted_handler = _get_or_add_default_handler(logger)
        setted_handler.setLevel(log_level)
        setted_handler.setFormatter(formatter)

    CORE_LOGGER.info("loggers initialized.")
