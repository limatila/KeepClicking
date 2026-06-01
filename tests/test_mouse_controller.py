from src.core.dataclasses import MouseCommand
from src.core.config import get_config
from src.core.choices import MouseCommandAction

import src.service.hardware_controller as mouse_controller_service


def test_mouse_controller_click(monkeypatch):
    calls = []

    def fake_click():
        calls.append("click")

    monkeypatch.setattr(mouse_controller_service.pag, "click", fake_click)

    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()
    
    result = controller.execute(MouseCommand(action=MouseCommandAction.CLICK), config)

    assert calls == ["click"]
    assert result.stopped is False
    assert result.error is None
    assert mouse_controller_service.pag.PAUSE == config.pyautogui_pause_seconds
    assert mouse_controller_service.pag.FAILSAFE == config.pyautogui_failsafe


def test_mouse_controller_stop():
    controller = mouse_controller_service.PyAutoGuiMouseController()
    config = get_config()
    
    result = controller.execute(MouseCommand(action=MouseCommandAction.STOP), config)
    
    assert result.stopped is True
    assert result.error is None
