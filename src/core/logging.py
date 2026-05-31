"""Logging configuration utilities."""

from __future__ import annotations

import logging
from logging import DEBUG


core_logger = logging.getLogger('baseLogger.core')
core_logger.setLevel(DEBUG)

if not core_logger.handlers:
	handler = logging.StreamHandler()
	formatter = logging.Formatter(
		"%(asctime)s %(name)s %(levelname)s %(message)s"
	)
	handler.setFormatter(formatter)
	core_logger.addHandler(handler)

core_logger.propagate = False

for child in ("runner", "parser", "validator", "mouse"):
	logging.getLogger(f"baseLogger.{child}")

core_logger.info("core loggers initialized")