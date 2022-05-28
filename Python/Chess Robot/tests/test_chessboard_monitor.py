from pathlib import Path

from PIL import Image

from src.api import Square
from src.chessboard_coordinates import ChessboardCoordinates
from src.chessboard_monitor import ChessboardMonitor

from .helpers import get_moves_from_game

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"

COORDS_WHITE_LICHESS = ChessboardCoordinates(
    left_top=(541, 225),
    right_bottom=(1164, 854),
    our_piece_colour="white",
)
COORDS_BLACK_LICHESS = ChessboardCoordinates(
    left_top=(541, 225),
    right_bottom=(1164, 854),
    our_piece_colour="black",
)

highlighted_colours_lichess = [
    (205, 210, 106),
    (170, 162, 58),
]

MONITOR_WHITE_LICHESS = ChessboardMonitor(
    COORDS_WHITE_LICHESS, highlighted_colours_lichess
)
MONITOR_BLACK_LICHESS = ChessboardMonitor(
    COORDS_BLACK_LICHESS, highlighted_colours_lichess
)


def _test_highlight_monitor(folder: Path, monitor: ChessboardMonitor):
    game_file = folder / "game.pgn"
    game_moves = get_moves_from_game(game_file.read_text())
    for move, img in zip(game_moves, folder.glob("*.png")):
        screen = Image.open(img)
        highlighted_squares = monitor.get_highlighted_squares(screen)
        possible_square_moves = [
            highlighted_squares[0].coordination + highlighted_squares[1].coordination,
            highlighted_squares[1].coordination + highlighted_squares[0].coordination,
        ]
        assert move in possible_square_moves


def test_highlight_lichess_white():
    folder = IMG / "lichess" / "white"
    _test_highlight_monitor(folder, MONITOR_WHITE_LICHESS)


def test_highlight_lichess_black():
    folder = IMG / "lichess" / "black"
    _test_highlight_monitor(folder, MONITOR_BLACK_LICHESS)


def _test_squares_are_highlighted(
    img: Path, squares: list[Square], monitor: ChessboardMonitor, result: bool
):
    screen = Image.open(img)
    assert result == monitor.check_if_squares_are_highlighted(screen, squares)


def test_check_if_squares_are_highlighted_white():
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "white" / "0001.png",
        squares=[Square("e2")],
        monitor=MONITOR_WHITE_LICHESS,
        result=True,
    )
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "white" / "0001.png",
        squares=[Square("e2")],
        monitor=MONITOR_WHITE_LICHESS,
        result=True,
    )
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "white" / "0001.png",
        squares=[Square("e2"), Square("e4")],
        monitor=MONITOR_WHITE_LICHESS,
        result=True,
    )

    _test_squares_are_highlighted(
        img=IMG / "lichess" / "white" / "0001.png",
        squares=[Square("c5")],
        monitor=MONITOR_WHITE_LICHESS,
        result=False,
    )
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "white" / "0001.png",
        squares=[Square("e2"), Square("e4"), Square("e5")],
        monitor=MONITOR_WHITE_LICHESS,
        result=False,
    )


def test_check_if_squares_are_highlighted_black():
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "black" / "0005.png",
        squares=[Square("b1")],
        monitor=MONITOR_BLACK_LICHESS,
        result=True,
    )
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "black" / "0005.png",
        squares=[Square("c3")],
        monitor=MONITOR_BLACK_LICHESS,
        result=True,
    )
    _test_squares_are_highlighted(
        img=IMG / "lichess" / "black" / "0005.png",
        squares=[Square("c3"), Square("b1")],
        monitor=MONITOR_BLACK_LICHESS,
        result=True,
    )

    _test_squares_are_highlighted(
        img=IMG / "lichess" / "black" / "0005.png",
        squares=[Square("c5")],
        monitor=MONITOR_BLACK_LICHESS,
        result=False,
    )
