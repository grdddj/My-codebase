import pytest

from src.api import Square
from src.chessboard_coordinates import ChessboardCoordinates

COORDS = ChessboardCoordinates(
    left_top=(300, 300),
    right_bottom=(900, 900),
    our_piece_colour="white",
)

COORDS_BLACK = ChessboardCoordinates(
    left_top=(300, 300),
    right_bottom=(900, 900),
    our_piece_colour="black",
)


def test_invalid_colour():
    with pytest.raises(AssertionError, match="Invalid colour"):
        ChessboardCoordinates(
            left_top=(300, 300),
            right_bottom=(900, 900),
            our_piece_colour="invalid",  # type: ignore
        )


def test_invalid_cooordinates():
    with pytest.raises(AssertionError, match="Invalid square size. Check coordinates"):
        ChessboardCoordinates(
            left_top=(900, 900),
            right_bottom=(300, 300),
            our_piece_colour="white",
        )

    with pytest.raises(AssertionError, match="Invalid square size. Check coordinates"):
        ChessboardCoordinates(
            left_top=(300, 300),
            right_bottom=(307, 307),
            our_piece_colour="white",
        )


def test_get_square_center_white():
    assert COORDS.get_square_center(Square("a1")) == (337, 862)
    assert COORDS.get_square_center(Square("a8")) == (337, 337)
    assert COORDS.get_square_center(Square("h1")) == (862, 862)
    assert COORDS.get_square_center(Square("h8")) == (862, 337)
    assert COORDS.get_square_center(Square("d4")) == (562, 637)
    assert COORDS.get_square_center(Square("d5")) == (562, 562)


def test_get_square_center_black():
    assert COORDS_BLACK.get_square_center(Square("a1")) == (862, 337)
    assert COORDS_BLACK.get_square_center(Square("a8")) == (862, 862)
    assert COORDS_BLACK.get_square_center(Square("h1")) == (337, 337)
    assert COORDS_BLACK.get_square_center(Square("h8")) == (337, 862)
    assert COORDS_BLACK.get_square_center(Square("d4")) == (637, 562)
    assert COORDS_BLACK.get_square_center(Square("d5")) == (637, 637)


def test_get_all_square_items():
    square_items = COORDS.get_all_square_items()
    assert len(list(square_items)) == 64
    square_items = COORDS_BLACK.get_all_square_items()
    assert len(list(square_items)) == 64


def test_get_square_size():
    assert COORDS.get_square_size() == 600 // 8
    assert COORDS_BLACK.get_square_size() == 600 // 8


def test_get_square_center_invalid_square():
    with pytest.raises(ValueError, match="does not exist"):
        COORDS.get_square_center("a1")  # type: ignore
