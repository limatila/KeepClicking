"""Logging configuration utilities."""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> logging.Logger:
	"""Configure and return the base logger for the application."""

	base_logger = logging.getLogger("baseLogger")
	base_logger.setLevel(level)
	if not base_logger.handlers:
		handler = logging.StreamHandler()
		formatter = logging.Formatter(
			"%(asctime)s %(name)s %(levelname)s %(message)s"
		)
		handler.setFormatter(formatter)
		base_logger.addHandler(handler)
	base_logger.propagate = False

	for child in ("runner", "parser", "validator", "mouse"):
		logging.getLogger(f"baseLogger.{child}")

	return base_logger
