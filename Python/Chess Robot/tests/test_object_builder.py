import src.object_builder
from src.chessboard_assigner import ChessboardAssigner
from src.object_builder import (
    _debug,
    _force_boundaries_update,
    _mode,
    _observer_only_mode,
    _trigger_moves_manually,
    _website,
    get_config,
    get_robot,
)


def test_cmdline_parsing_defaults(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py"])
    assert _website() == "lichess"
    assert _mode() == "superblitz"
    assert not _observer_only_mode()
    assert not _debug()
    assert not _force_boundaries_update()
    assert not _trigger_moves_manually()


def test_cmdline_parsing_user_values(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "observe", "force", "trigger", "debug", "blitz", "kurnik"],
    )
    assert _website() == "kurnik"
    assert _mode() == "blitz"
    assert _observer_only_mode()
    assert _debug()
    assert _force_boundaries_update()
    assert _trigger_moves_manually()


def test_get_config(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "observe", "trigger", "debug", "blitz", "kurnik"],
    )
    config = get_config()
    assert config.website == "kurnik"
    assert config.mode == "blitz"
    assert config.observer_only_mode
    assert config.debug
    assert config.trigger_moves_manually
    assert not config.force_boundaries_update


def test_get_config_force(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "force", "slow", "chess.com"],
    )

    monkeypatch.setattr(
        ChessboardAssigner,
        "get_left_top_and_right_bottom_chessboard_pixels",
        lambda *args, **kwargs: ((300, 300), (900, 900)),
    )
    monkeypatch.setattr(
        src.object_builder,
        "save_new_boundaries_into_config",
        lambda *args, **kwargs: print("saving"),
    )

    config = get_config()
    assert config.website == "chess.com"
    assert config.mode == "slow"
    assert not config.observer_only_mode
    assert not config.debug
    assert not config.trigger_moves_manually
    assert config.force_boundaries_update
    assert config.chessboard_left_top_pixel == (300, 300)
    assert config.chessboard_right_bottom_pixel == (900, 900)


def test_get_robot():
    config = get_config()
    robot = get_robot(config, "white")
    assert hasattr(robot, "_analysis")
