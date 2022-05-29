import pyautogui

from src.api import Move, Square
from src.chessboard_coordinates import ChessboardCoordinates
from src.chessboard_player import ChessboardPlayer


def test_play(monkeypatch):
    COORDS = ChessboardCoordinates(
        left_top=(300, 300),
        right_bottom=(900, 900),
        our_piece_colour="white",
    )
    PLAYER = ChessboardPlayer(COORDS)

    click_coordinations = []

    def mock_click(x, y):
        click_coordinations.append((x, y))

    monkeypatch.setattr(pyautogui, "click", mock_click)

    from_square = Square("e2")
    to_square = Square("e4")

    initial_mouse_position = pyautogui.position()
    PLAYER.play_move(from_square + to_square)

    assert click_coordinations == [
        COORDS.get_square_center(from_square),
        COORDS.get_square_center(to_square),
        initial_mouse_position,
    ]


def test_play_promotion(monkeypatch):
    COORDS = ChessboardCoordinates(
        left_top=(300, 300),
        right_bottom=(900, 900),
        our_piece_colour="black",
    )
    PLAYER = ChessboardPlayer(COORDS)

    click_coordinations = []

    def mock_click(x, y):
        click_coordinations.append((x, y))

    monkeypatch.setattr(pyautogui, "click", mock_click)

    from_square = Square("c2")
    to_square = Square("c1")

    initial_mouse_position = pyautogui.position()
    PLAYER.play_move(Move("c2c1q"))

    assert click_coordinations == [
        COORDS.get_square_center(from_square),
        COORDS.get_square_center(to_square),
        COORDS.get_square_center(to_square),
        initial_mouse_position,
    ]
