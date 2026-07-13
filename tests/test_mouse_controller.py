from src.core.dataclasses import MouseCommand
from src.core.config import get_config
from src.core.choices import CommandDirection, MouseCommandAction

import src.service.hardware_controller as mouse_controller_service


def test_mouse_controller_click(monkeypatch):
    calls = []

    def fake_click(*args, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(mouse_controller_service.pag, "click", fake_click)

    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()

    result = controller.execute(MouseCommand(action=MouseCommandAction.CLICK), config)

    assert calls == [{"clicks": 1, "interval": 0.05, "button": "primary"}]
    assert result.stopped is False
    assert result.error is None
    assert mouse_controller_service.pag.PAUSE == config.pyautogui_pause_seconds
    assert mouse_controller_service.pag.FAILSAFE == config.pyautogui_failsafe


def test_mouse_controller_double_click(monkeypatch):
    calls = []

    def fake_click(*args, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(mouse_controller_service.pag, "click", fake_click)

    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()

    result = controller.execute(
        MouseCommand(action=MouseCommandAction.DOUBLE_CLICK),
        config,
    )

    assert calls == [{"clicks": 2, "interval": 0.05, "button": "primary"}]
    assert result.stopped is False
    assert result.error is None


def test_mouse_controller_right_click(monkeypatch):
    calls = []

    def fake_click(*args, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(mouse_controller_service.pag, "click", fake_click)

    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()

    result = controller.execute(
        MouseCommand(action=MouseCommandAction.RIGHT_CLICK),
        config,
    )

    assert calls == [{"clicks": 1, "interval": 0.05, "button": "right"}]
    assert result.stopped is False
    assert result.error is None


def test_mouse_controller_scroll_down(monkeypatch):
    scroll_calls = []

    def fake_scroll(amount):
        scroll_calls.append(amount)

    monkeypatch.setattr(mouse_controller_service.pag, "scroll", fake_scroll)

    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()

    result = controller.execute(
        MouseCommand(
            action=MouseCommandAction.SCROLL,
            direction=CommandDirection.DOWN,
            amount=300,
        ),
        config,
    )

    assert scroll_calls == [-300]
    assert result.stopped is False
    assert result.error is None


def test_mouse_controller_stop():
    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()

    result = controller.execute(MouseCommand(action=MouseCommandAction.STOP), config)

    assert result.stopped is True
    assert result.error is None


def test_mouse_controller_does_not_keep_stop_state(monkeypatch):
    calls = []

    def fake_click(*args, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(mouse_controller_service.pag, "click", fake_click)

    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()

    stopped = controller.execute(MouseCommand(action=MouseCommandAction.STOP), config)
    clicked = controller.execute(MouseCommand(action=MouseCommandAction.CLICK), config)

    assert stopped.stopped is True
    assert clicked.stopped is False
    assert clicked.error is None
    assert calls == [{"clicks": 1, "interval": 0.05, "button": "primary"}]
