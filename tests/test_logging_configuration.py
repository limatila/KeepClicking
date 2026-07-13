from logging import DEBUG, INFO

import src.core.config as config_module
import src.core.logging as logging_module
from src.core.config import get_config


def test_configure_logging_uses_runtime_override_over_env(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "false"}),
    )

    config = get_config(debug_mode=True)
    logging_module.configure_logging(config)

    assert logging_module.CORE_LOGGER.level == DEBUG
    assert logging_module.CORE_LOGGER.handlers[0].level == DEBUG


def test_configure_logging_respects_non_debug_runtime_config(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "true"}),
    )

    config = get_config(debug_mode=False)
    logging_module.configure_logging(config)

    assert logging_module.CORE_LOGGER.level == INFO
    assert logging_module.CORE_LOGGER.handlers[0].level == INFO


def test_configure_logging_is_idempotent():
    config = get_config(debug_mode=True)

    logging_module.configure_logging(config)
    first_count = len(logging_module.CORE_LOGGER.handlers)

    logging_module.configure_logging(config)
    second_count = len(logging_module.CORE_LOGGER.handlers)

    assert first_count == second_count == 1


def test_get_config_parses_false_boolean_from_env(monkeypatch):
    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "false", "pyautogui_failsafe": "false"}),
    )

    config = get_config()

    assert config.debug_mode is False
    assert config.pyautogui_failsafe is False
