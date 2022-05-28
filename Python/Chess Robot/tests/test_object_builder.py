from src.object_builder import (
    _force_boundaries_update,
    _mode,
    _observer_only_mode,
    _trigger_moves_manually,
    _website,
)


def test_cmdline_parsing_defaults(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py"])
    assert _website() == "lichess"
    assert _mode() == "superblitz"
    assert not _observer_only_mode()
    assert not _force_boundaries_update()
    assert not _trigger_moves_manually()


def test_cmdline_parsing_user_values(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["main.py", "observe", "force", "trigger", "blitz", "kurnik"]
    )
    assert _website() == "kurnik"
    assert _mode() == "blitz"
    assert _observer_only_mode()
    assert _force_boundaries_update()
    assert _trigger_moves_manually()
