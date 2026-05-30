import src.service.mouse_controller as mouse_controller
from src.core.config import get_config
from src.core.models import Command, CommandAction


def test_mouse_controller_click(monkeypatch):
    calls = []

    def fake_click():
        calls.append("click")

    monkeypatch.setattr(mouse_controller.pyautogui, "click", fake_click)

    controller = mouse_controller.PyAutoGuiMouseController()
    config = get_config()
    result = controller.execute(Command(action=CommandAction.CLICK), config)

    assert calls == ["click"]
    assert result.stopped is False
    assert result.error is None
    assert mouse_controller.pyautogui.PAUSE == config.pyautogui_pause_seconds
    assert mouse_controller.pyautogui.FAILSAFE == config.pyautogui_failsafe


def test_mouse_controller_stop():
    controller = mouse_controller.PyAutoGuiMouseController()
    config = get_config()
    result = controller.execute(Command(action=CommandAction.STOP), config)
    assert result.stopped is True
    assert result.error is None
