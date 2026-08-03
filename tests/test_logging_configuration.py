from __future__ import annotations

from pathlib import Path

import pytest

import src.core.config as config_module
import src.core.logging as logging_module
from src.core.config import AppConfig, get_config


def _reset_logging_state() -> None:
    for logger in logging_module.ALL_LOGGERS:
        for handler in tuple(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

    logging_module._ACTIVE_FILE_HANDLER = None
    logging_module._ACTIVE_RUNTIME_LOG_PATH = None


@pytest.fixture(autouse=True)
def reset_logging_state():
    _reset_logging_state()
    yield
    _reset_logging_state()


def _find_handler(logger, handler_name: str):
    return next(
        handler
        for handler in logger.handlers
        if getattr(handler, "name", "") == handler_name
    )


def test_configure_logging_uses_runtime_override_over_env(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "false"}),
    )

    config = get_config(debug_mode=True)
    logging_module.configure_logging(config)

    stream_handler = _find_handler(
        logging_module.CORE_LOGGER,
        logging_module.DEFAULT_HANDLER_NAME,
    )

    assert logging_module.CORE_LOGGER.level == logging_module.DEBUG
    assert stream_handler.level == logging_module.DEBUG
    assert all(
        getattr(handler, "name", "") != logging_module.DEFAULT_FILE_HANDLER_NAME
        for handler in logging_module.CORE_LOGGER.handlers
    )


def test_configure_logging_respects_non_debug_runtime_config(monkeypatch, tmp_path):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "true"}),
    )
    config = AppConfig(debug_mode=False, runtime_dir=tmp_path)
    logging_module.configure_logging(config)

    stream_handler = _find_handler(
        logging_module.CORE_LOGGER,
        logging_module.DEFAULT_HANDLER_NAME,
    )
    file_handler = _find_handler(
        logging_module.CORE_LOGGER,
        logging_module.DEFAULT_FILE_HANDLER_NAME,
    )

    assert logging_module.CORE_LOGGER.level == logging_module.INFO
    assert stream_handler.level == logging_module.INFO
    assert file_handler.level == logging_module.INFO
    assert Path(file_handler.baseFilename) == tmp_path / "logs" / "runtime_1.log"


def test_configure_logging_is_idempotent(tmp_path):
    config = AppConfig(debug_mode=False, runtime_dir=tmp_path)

    logging_module.configure_logging(config)
    first_handlers = tuple(logging_module.CORE_LOGGER.handlers)

    logging_module.configure_logging(config)
    second_handlers = tuple(logging_module.CORE_LOGGER.handlers)

    assert len(first_handlers) == len(second_handlers) == 2
    assert first_handlers == second_handlers
    assert logging_module._ACTIVE_RUNTIME_LOG_PATH == tmp_path / "logs" / "runtime_1.log"


def test_configure_logging_creates_incremented_run_logs(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True)
    (log_dir / "runtime_1.log").write_text("old\n", encoding="utf-8")
    (log_dir / "runtime_2.log").write_text("old\n", encoding="utf-8")

    logging_module.configure_logging(AppConfig(debug_mode=False, runtime_dir=tmp_path))

    assert logging_module._ACTIVE_RUNTIME_LOG_PATH == log_dir / "runtime_3.log"


def test_configure_logging_in_debug_mode_starts_without_a_file_handler(tmp_path):
    logging_module.configure_logging(AppConfig(debug_mode=True, runtime_dir=tmp_path))

    assert all(
        getattr(handler, "name", "") != logging_module.DEFAULT_FILE_HANDLER_NAME
        for handler in logging_module.CORE_LOGGER.handlers
    )
    assert logging_module._ACTIVE_FILE_HANDLER is None
    assert logging_module._ACTIVE_RUNTIME_LOG_PATH is None


def test_get_config_parses_false_boolean_from_env(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "false", "pyautogui_failsafe": "false"}),
    )

    config = get_config()

    assert config.debug_mode is False
    assert config.pyautogui_failsafe is False
