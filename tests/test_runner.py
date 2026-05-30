import logging

from src.commands.normalizer import normalize_text
from src.commands.parser import RuleBasedCommandParser
from src.commands.validator import RuleBasedCommandValidator
from src.core.config import get_config
from src.core.models import CommandAction
from src.service.mouse_controller import ExecutionResult
from src.service.runner import ApplicationRunner


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
        if command.action == CommandAction.STOP:
            return ExecutionResult(stopped=True, error=None)
        return ExecutionResult(stopped=False, error=None)


def test_runner_executes_commands():
    adapter = FakeAdapter(["click", "stop"])
    controller = FakeController()
    logger = logging.getLogger("test.runner")
    logger.addHandler(logging.NullHandler())

    runner = ApplicationRunner(
        adapter=adapter,
        normalizer=normalize_text,
        parser=RuleBasedCommandParser(),
        validator=RuleBasedCommandValidator(),
        controller=controller,
        config=get_config(),
        logger=logger,
    )

    runner.run()

    assert controller.seen == [CommandAction.CLICK, CommandAction.STOP]
    assert adapter.closed is True
