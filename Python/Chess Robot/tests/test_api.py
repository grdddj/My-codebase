import pytest

from src.api import Move, Square


def test_invalid_square():
    with pytest.raises(AssertionError, match="Second coordinate must be 1-8"):
        Square("a9")

    with pytest.raises(AssertionError, match="First coordinate must be a-h"):
        Square("i8")

    with pytest.raises(AssertionError, match="Square must be 2 characters long"):
        Square("ab3")


def test_valid_square():
    assert Square("a1").coordination == "a1"
    assert Square("h8").coordination == "h8"


def test_add_two_squares():
    assert Square("a1") + Square("h8") == Move("a1h8")
    assert Square("g1") + Square("f3") == Move("g1f3")


def test_add_two_squares_nonsquare():
    with pytest.raises(AssertionError, match="Can only add two Squares together"):
        Square("g1") + "f3"  # type: ignore


def test_move_valid():
    move = Move("a1h8")
    assert move.from_square.coordination == "a1"
    assert move.to_square.coordination == "h8"
    assert move.promotion is None

    move = Move("c2c1Q")
    assert move.from_square.coordination == "c2"
    assert move.to_square.coordination == "c1"
    assert move.promotion == "Q"

    move = Move("f7f8N")
    assert move.from_square.coordination == "f7"
    assert move.to_square.coordination == "f8"
    assert move.promotion == "N"


def test_move_invalid():
    with pytest.raises(AssertionError, match="Move must have 4 or 5 characters"):
        Move("c5")
    with pytest.raises(AssertionError, match="Move must have 4 or 5 characters"):
        Move("c1c2c3")
    with pytest.raises(AssertionError, match="Move must have 4 or 5 characters"):
        Move("g8f")

    with pytest.raises(AssertionError, match="Cannot move from a square to itself"):
        Move("f4f4")

    with pytest.raises(AssertionError, match="Invalid promotion piece"):
        Move("d7d8A")

    with pytest.raises(AssertionError, match="Can only promote on first/last row"):
        Move("b6b7Q")
