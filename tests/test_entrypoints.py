import src.cli as cli_module
import src.main as main_module
import src.core.config as config_module


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
