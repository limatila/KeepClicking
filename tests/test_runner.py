import logging

from src.core.config import get_config
from src.core.choices import MouseCommandAction

from src.command_mapper.normalizer import normalize_text
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


def test_runner_executes_commands():
    adapter = FakeAdapter(["click", "stop"])
    controller = FakeController()
    logger = logging.getLogger("test.runner")
    logger.addHandler(logging.NullHandler())

    runner = MouseApplicationRunner(
        adapter=adapter,
        normalizer=normalize_text,
        parser=MouseCommandParser(),
        validator=MouseCommandValidator(),
        controller=controller,
        config=get_config(),
        logger=logger,
    )

    runner.run()

    assert controller.seen == [MouseCommandAction.CLICK, MouseCommandAction.STOP]
    assert adapter.closed is True
