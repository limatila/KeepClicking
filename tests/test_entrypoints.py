from pathlib import Path

import src.cli as cli_module
import src.main as main_module
import src.core.config as config_module
import src.command_mapper.normalizer_dispatchers as normalizer_dispatchers_module
import src.command_mapper.parser as parser_module
import src.command_mapper.validator as validator_module
import src.service.application_runner as application_runner_module
import src.service.hardware_controller as hardware_controller_module
import src.speech.offline_adapters.offline_vosk_adapter as offline_vosk_adapter_module
import src.speech.wakeword.engine as wakeword_engine_module
from src.core.choices import SpeechLanguage
from src.core.config import get_default_offline_model_path


class FakeCommandResult:
    def __init__(self, should_dispatch: bool, exit_code: int = 0):
        self.should_dispatch = should_dispatch
        self.exit_code = exit_code
        self.dispatch_calls = 0

    def dispatch(self) -> int:
        self.dispatch_calls += 1
        return self.exit_code


def test_cli_main_dispatches_one_off_command_without_running_app(monkeypatch):
    command = FakeCommandResult(should_dispatch=True, exit_code=7)
    run_calls = {"count": 0}

    monkeypatch.setattr(cli_module, "resolve_cli_command", lambda argv, config: command)
    monkeypatch.setattr(cli_module, "configure_logging", lambda config: None)
    monkeypatch.setattr(
        cli_module,
        "run_application",
        lambda config: run_calls.__setitem__("count", run_calls["count"] + 1),
    )

    result = cli_module.main(["--list-audio-devices"])

    assert result == 7
    assert command.dispatch_calls == 1
    assert run_calls["count"] == 0


def test_cli_main_runs_application_when_no_one_off_command(monkeypatch):
    command = FakeCommandResult(should_dispatch=False)
    seen = {"debug_mode": None}

    monkeypatch.setattr(cli_module, "resolve_cli_command", lambda argv, config: command)
    monkeypatch.setattr(cli_module, "configure_logging", lambda config: None)
    monkeypatch.setattr(
        cli_module,
        "run_application",
        lambda config: seen.__setitem__("debug_mode", config.debug_mode) or 0,
    )

    result = cli_module.main([])

    assert result == 0
    assert seen["debug_mode"] is True


def test_cli_main_loads_project_env_file(monkeypatch, tmp_path):
    command = FakeCommandResult(should_dispatch=False)
    seen = {}
    local_env_path = tmp_path / ".env"
    local_env_path.write_text("mouse_movement_pixels=321\n", encoding="utf-8")

    monkeypatch.setattr(cli_module, "ROOT_PATH", tmp_path)
    monkeypatch.setattr(cli_module, "resolve_cli_command", lambda argv, config: command)
    monkeypatch.setattr(cli_module, "configure_logging", lambda config: None)
    monkeypatch.setattr(
        cli_module,
        "run_application",
        lambda config: seen.update(
            {
                "debug_mode": config.debug_mode,
                "env_path": config.env_path,
                "mouse_movement_pixels": config.mouse_movement_pixels,
            }
        )
        or 0,
    )

    result = cli_module.main([])

    assert result == 0
    assert seen == {
        "debug_mode": True,
        "env_path": local_env_path.resolve(),
        "mouse_movement_pixels": 321,
    }


def test_main_dispatches_one_off_command_without_running_app(monkeypatch):
    command = FakeCommandResult(should_dispatch=True, exit_code=5)
    run_calls = {"count": 0}

    monkeypatch.setattr(main_module, "resolve_cli_command", lambda argv, config: command)
    monkeypatch.setattr(main_module, "configure_logging", lambda config: None)
    monkeypatch.setattr(
        main_module,
        "run_application",
        lambda config: run_calls.__setitem__("count", run_calls["count"] + 1),
    )

    result = main_module.main(["--list-audio-devices"])

    assert result == 5
    assert command.dispatch_calls == 1
    assert run_calls["count"] == 0


def test_main_runs_application_when_no_one_off_command(monkeypatch):
    command = FakeCommandResult(should_dispatch=False)
    seen = {"debug_mode": None}

    monkeypatch.setattr(
        config_module.AppConfig,
        "read_env_values",
        staticmethod(lambda: {"debug_mode": "false"}),
    )
    monkeypatch.setattr(main_module, "resolve_cli_command", lambda argv, config: command)
    monkeypatch.setattr(main_module, "configure_logging", lambda config: None)
    monkeypatch.setattr(
        main_module,
        "run_application",
        lambda config: seen.__setitem__("debug_mode", config.debug_mode) or 0,
    )

    result = main_module.main([])

    assert result == 0
    assert seen["debug_mode"] is False


def test_build_application_runner_uses_pt_br_normalizer_and_default_vosk_model(monkeypatch):
    seen = {}
    normalizer = object()
    parser = object()
    validator = object()
    controller = object()

    class FakeWakeWordEngine:
        def __init__(self, config):
            seen["wakeword_config"] = config

    class FakeAdapter:
        def __init__(self, config, wake_word_engine):
            seen["adapter_config"] = config
            seen["wake_word_engine"] = wake_word_engine

    class FakeRunner:
        def __init__(self, adapter, normalizer, parser, validator, controller, config):
            seen["adapter"] = adapter
            seen["normalizer"] = normalizer
            seen["parser"] = parser
            seen["validator"] = validator
            seen["controller"] = controller
            seen["config"] = config

    monkeypatch.setattr(
        normalizer_dispatchers_module,
        "resolve_command_normalizer",
        lambda language: seen.__setitem__("language", language) or normalizer,
    )
    monkeypatch.setattr(parser_module, "MouseCommandParser", lambda: parser)
    monkeypatch.setattr(validator_module, "MouseCommandValidator", lambda: validator)
    monkeypatch.setattr(
        hardware_controller_module,
        "PyAutoGuiMouseController",
        lambda: controller,
    )
    monkeypatch.setattr(
        wakeword_engine_module,
        "OpenWakeWordEngine",
        FakeWakeWordEngine,
    )
    monkeypatch.setattr(
        offline_vosk_adapter_module,
        "VoskSpeechAdapter",
        FakeAdapter,
    )
    monkeypatch.setattr(
        application_runner_module,
        "MouseApplicationRunner",
        FakeRunner,
    )

    config = config_module.get_config(
        speech_language=SpeechLanguage.PT_BR,
        audio_input_device=None,
    )
    runner = main_module.build_application_runner(config)

    assert isinstance(runner, FakeRunner)
    assert seen["language"] == SpeechLanguage.PT_BR
    assert seen["normalizer"] is normalizer
    assert seen["adapter"] is not None
    assert Path(seen["adapter_config"].offline_model_path) == get_default_offline_model_path(
        SpeechLanguage.PT_BR
    )
