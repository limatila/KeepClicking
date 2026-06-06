from src.command_mapper.normalizer import normalize_text


def test_normalize_click():
    assert normalize_text(" Click ") == "click"


def test_normalize_double_click():
    assert normalize_text("double-click") == "double click"


def test_normalize_synonym():
    assert normalize_text("clique") == "click"
