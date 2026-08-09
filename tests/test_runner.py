import logging
import pytest

from src.command_mapper.normalizers.english import EnglishSpeechNormalizer
from src.core.config import get_config
from src.core.errors import AdapterError
from src.core.choices import MouseCommandAction

from src.command_mapper.parser import MouseCommandParser
from src.command_mapper.validator import MouseCommandValidator
from src.service.dataclasses import MouseExecutionResult
from src.service.application_runner import MouseApplicationRunner


class FakeAdapter:
    def __init__(self, items):
        self._items = list(items)
        self.closed = False

    def next_text(self):
        if not self._items:
            return None
        return self._items.pop(0)

    def close(self):
        self.closed = True


class FakeController:
    def __init__(self):
        self.seen = []

    def execute(self, command, config):
        self.seen.append(command.action)
        if command.action == MouseCommandAction.STOP:
            return MouseExecutionResult(stopped=True, error=None)
        return MouseExecutionResult(stopped=False, error=None)


class FakeNotificationSoundPlayer:
    def __init__(self, error_method: str | None = None, error: Exception | None = None):
        self.calls = []
        self.error_method = error_method
        self.error = error

    def _record_call(self, method_name: str) -> None:
        self.calls.append(method_name)
        if self.error_method == method_name and self.error is not None:
            raise self.error

    def play_wake_word_detected(self):
        self._record_call("wake_word_detected")

    def play_runner_started(self):
        self._record_call("runner_started")

    def play_runner_finished(self):
        self._record_call("runner_finished")

    def play_application_error(self):
        self._record_call("application_error")

    def play_speech_error(self):
        self._record_call("speech_error")

    def play_parse_error(self):
        self._record_call("parse_error")

    def play_click(self):
        self._record_call("click")


def test_runner_listen_and_execute_executes_commands(monkeypatch):
    adapter = FakeAdapter(["click", "stop"])
    controller = FakeController()
    notification_sound_player = FakeNotificationSoundPlayer()
    logger = logging.getLogger("test.runner")
    logger.addHandler(logging.NullHandler())
    monkeypatch.setattr(
        "src.service.application_runner.build_notification_sound_player",
        lambda: notification_sound_player,
    )

    runner = MouseApplicationRunner(
        adapter=adapter,
        normalizer=EnglishSpeechNormalizer(),
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=controller,
        config=get_config(),
        logger=logger,
    )

    runner.listen_and_execute()

    assert controller.seen == [MouseCommandAction.CLICK, MouseCommandAction.STOP]
    assert adapter.closed is False
    assert notification_sound_player.calls == []


def test_runner_listen_and_execute_continues_after_parse_error(monkeypatch):
    adapter = FakeAdapter(["nonsense", "click", "stop"])
    controller = FakeController()
    notification_sound_player = FakeNotificationSoundPlayer()
    logger = logging.getLogger("test.runner.parse_error")
    logger.addHandler(logging.NullHandler())
    monkeypatch.setattr(
        "src.service.application_runner.build_notification_sound_player",
        lambda: notification_sound_player,
    )

    runner = MouseApplicationRunner(
        adapter=adapter,
        normalizer=EnglishSpeechNormalizer(),
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=controller,
        config=get_config(),
        logger=logger,
    )

    runner.listen_and_execute()

    assert controller.seen == [MouseCommandAction.CLICK, MouseCommandAction.STOP]
    assert notification_sound_player.calls == ["parse_error"]


def test_runner_run_plays_start_and_finish_sounds(monkeypatch):
    adapter = FakeAdapter(["click"])
    controller = FakeController()
    notification_sound_player = FakeNotificationSoundPlayer()
    logger = logging.getLogger("test.runner.adapter_end")
    logger.addHandler(logging.NullHandler())
    monkeypatch.setattr(
        "src.service.application_runner.build_notification_sound_player",
        lambda: notification_sound_player,
    )

    runner = MouseApplicationRunner(
        adapter=adapter,
        normalizer=EnglishSpeechNormalizer(),
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=controller,
        config=get_config(),
        logger=logger,
    )

    runner.run()

    assert controller.seen == [MouseCommandAction.CLICK]
    assert adapter.closed is True
    assert notification_sound_player.calls == ["runner_started", "runner_finished"]


def test_runner_run_logs_and_finishes_when_start_sound_fails(monkeypatch):
    notification_sound_player = FakeNotificationSoundPlayer(
        error_method="runner_started",
        error=RuntimeError("boom"),
    )
    logger = logging.getLogger("test.runner.fatal")
    logger.addHandler(logging.NullHandler())
    monkeypatch.setattr(
        "src.service.application_runner.build_notification_sound_player",
        lambda: notification_sound_player,
    )

    adapter = FakeAdapter(["click"])
    runner = MouseApplicationRunner(
        adapter=adapter,
        normalizer=EnglishSpeechNormalizer(),
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=FakeController(),
        config=get_config(),
        logger=logger,
    )

    with pytest.raises(RuntimeError, match="boom"):
        runner.run()

    assert adapter.closed is True
    assert notification_sound_player.calls == [
        "runner_started",
        "application_error",
        "runner_finished",
    ]
