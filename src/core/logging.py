"""Logging configuration utilities."""

from __future__ import annotations

import logging
from logging import DEBUG, INFO
from pathlib import Path

from src.core.config import AppConfig

DEFAULT_HANDLER_NAME = "keepclicking_stream_handler"
DEFAULT_FILE_HANDLER_NAME = "keepclicking_file_handler"
DEFAULT_FILE_LOG_PREFIX = "runtime_"

_ACTIVE_FILE_HANDLER: logging.FileHandler | None = None
_ACTIVE_RUNTIME_LOG_PATH: Path | None = None


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


def _get_next_runtime_log_path(log_dir: Path) -> Path:
    highest_run_index = 0
    
    for existing_log_path in log_dir.glob(f"{DEFAULT_FILE_LOG_PREFIX}*.log"):
        suffix = existing_log_path.stem.removeprefix(DEFAULT_FILE_LOG_PREFIX)
    
        if suffix.isdigit():
            highest_run_index = max(highest_run_index, int(suffix))
    
    return log_dir / f"{DEFAULT_FILE_LOG_PREFIX}{highest_run_index + 1}.log"


def _get_or_add_stream_handler(logger: logging.Logger) -> logging.Handler:
    for handler in logger.handlers:
        if getattr(handler, "name", "") == DEFAULT_HANDLER_NAME:
            return handler
    
    handler = logging.StreamHandler()
    handler.name = DEFAULT_HANDLER_NAME
    
    logger.addHandler(handler)
    
    return handler


def _get_or_add_file_handler(logger: logging.Logger, log_path: Path) -> logging.FileHandler:
    global _ACTIVE_FILE_HANDLER, _ACTIVE_RUNTIME_LOG_PATH
    
    if _ACTIVE_FILE_HANDLER is None:
        _ACTIVE_RUNTIME_LOG_PATH = log_path
    
        _ACTIVE_FILE_HANDLER = logging.FileHandler(log_path, encoding="utf-8")
        _ACTIVE_FILE_HANDLER.name = DEFAULT_FILE_HANDLER_NAME
    
    if _ACTIVE_FILE_HANDLER not in logger.handlers:
        logger.addHandler(_ACTIVE_FILE_HANDLER)
    
    return _ACTIVE_FILE_HANDLER


def configure_logging(config: AppConfig) -> None:
    """Configure package loggers using the effective runtime config."""
    log_level = DEBUG if config.debug_mode else INFO
    formatter = logging.Formatter(config.logging_format)

    file_log_path = _ACTIVE_RUNTIME_LOG_PATH or _get_next_runtime_log_path(config.log_dir)
    
    for logger in ALL_LOGGERS:
        logger.setLevel(log_level)
    
        logger.propagate = logger.name != CORE_LOGGER.name
    
        stream_handler = _get_or_add_stream_handler(logger)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
    
        if file_log_path is not None:
            file_handler = _get_or_add_file_handler(logger, file_log_path)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)

    CORE_LOGGER.info("loggers initialized.")
    
    if _ACTIVE_RUNTIME_LOG_PATH is not None:
        CORE_LOGGER.info("runtime log file: %s", _ACTIVE_RUNTIME_LOG_PATH)
