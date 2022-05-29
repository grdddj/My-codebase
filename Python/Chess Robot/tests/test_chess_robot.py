import threading
import time
from pathlib import Path
from typing import Literal

import pytest
from PIL import Image

import src.chess_robot
import src.helpers
from src.api import ChessResult, Move, Square
from src.chess_library import ChessLibrary
from src.chess_robot import (
    ChessRobot,
    NoNewMoveFoundOnTheChessboard,
    TheGameHasFinished,
)
from src.chessboard_coordinates import ChessboardCoordinates
from src.chessboard_monitor import ChessboardMonitor

from .helpers import get_moves_from_game, sleep_and_press_key
from .mock_config import MockConfig
from .mock_player import MockPlayer

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def get_robot(
    our_colour: Literal["white", "black"] = "white",
    observer_only_mode: bool = False,
    force_boundaries_update: bool = False,
    trigger_moves_manually: bool = False,
    website: str = "lichess",
    mode: str = "superblitz",
    debug: bool = False,
) -> ChessRobot:
    CONFIG = MockConfig(
        observer_only_mode=observer_only_mode,
        force_boundaries_update=force_boundaries_update,
        trigger_moves_manually=trigger_moves_manually,
        website=website,
        mode=mode,
        debug=debug,
    )
    COORDINATES = ChessboardCoordinates(
        left_top=CONFIG.chessboard_left_top_pixel,
        right_bottom=CONFIG.chessboard_right_bottom_pixel,
        our_piece_colour=our_colour,
    )
    MONITOR = ChessboardMonitor(
        chessboard_coordinates=COORDINATES,
        highlighted_colours=[
            CONFIG.white_field_highlight_colour,
            CONFIG.black_field_highlight_colour,
        ],
    )
    PLAYER = MockPlayer(COORDINATES)
    CHESS = ChessLibrary(our_colour, CONFIG.engine_location)

    return ChessRobot(
        chessboard_monitor=MONITOR,
        chessboard_player=PLAYER,
        chess_library=CHESS,
        config=CONFIG,
    )


def test_initial_setup():
    robot = get_robot()
    assert len(robot._chess_library.get_game_moves()) == 0
    assert robot._currently_highlighted_squares is None
    assert robot._our_last_move is None
    assert robot._move_done_on_the_board is None

    assert robot._analysis.mate_string is None
    assert robot._chess_library.is_valid_move(robot._best_move())
    assert 0 < robot._analysis.pawn_score < 0.5


def test_initial_setup_black():
    robot = get_robot(our_colour="black")
    assert -0.5 < robot._analysis.pawn_score < 0


def test_play_first_move_as_white_if_necessary():
    robot = get_robot(our_colour="white")
    robot._play_first_move_as_white_if_necessary()
    assert len(robot._chess_library.get_game_moves()) == 1
    assert robot._chess_library.get_game_moves()[0] == robot._best_move()
    assert robot._our_last_move == robot._best_move()
    assert robot._move_done_on_the_board is None

    # Does not do anything the second time
    robot._play_first_move_as_white_if_necessary()
    assert len(robot._chess_library.get_game_moves()) == 1


def test_play_first_move_as_white_if_necessary_black():
    robot = get_robot(our_colour="black")
    robot._play_first_move_as_white_if_necessary()
    assert len(robot._chess_library.get_game_moves()) == 0
    assert robot._our_last_move is None
    assert robot._move_done_on_the_board is None


def test_get_currently_highlighted_squares():
    robot = get_robot()
    assert robot._currently_highlighted_squares is None

    img = Image.open(IMG / "lichess" / "white" / "0001.png")
    robot._get_currently_highlighted_squares(img)
    assert robot._currently_highlighted_squares == (Square("e2"), Square("e4"))
    with pytest.raises(NoNewMoveFoundOnTheChessboard, match="Same highlight as before"):
        robot._get_currently_highlighted_squares(img)
    assert robot._currently_highlighted_squares == (Square("e2"), Square("e4"))

    img = Image.open(IMG / "lichess" / "white" / "0002.png")
    robot._get_currently_highlighted_squares(img)
    assert robot._currently_highlighted_squares == (Square("c6"), Square("c7"))
    with pytest.raises(NoNewMoveFoundOnTheChessboard, match="Same highlight as before"):
        robot._get_currently_highlighted_squares(img)
    assert robot._currently_highlighted_squares == (Square("c6"), Square("c7"))

    img = Image.open(IMG / "rainbow.jpg")
    with pytest.raises(NoNewMoveFoundOnTheChessboard, match="No highlight found"):
        robot._get_currently_highlighted_squares(img)
    assert robot._currently_highlighted_squares == (Square("c6"), Square("c7"))


def test_check_if_last_move_was_not_done_by_us():
    robot = get_robot()
    assert robot._currently_highlighted_squares is None
    assert robot._our_last_move is None
    robot._check_if_last_move_was_not_done_by_us()

    robot._currently_highlighted_squares = (Square("e2"), Square("e4"))
    robot._check_if_last_move_was_not_done_by_us()

    robot._our_last_move = Move("e2e4")
    with pytest.raises(NoNewMoveFoundOnTheChessboard, match="Last move was ours"):
        robot._check_if_last_move_was_not_done_by_us()

    robot._currently_highlighted_squares = (Square("c6"), Square("c7"))
    robot._check_if_last_move_was_not_done_by_us()


def test_recognize_move_done_on_the_board():
    robot = get_robot("black")
    assert robot._move_done_on_the_board is None
    with pytest.raises(AssertionError, match="No highlighted squares"):
        robot._recognize_move_done_on_the_board()

    robot._currently_highlighted_squares = (Square("e2"), Square("e4"))
    robot._recognize_move_done_on_the_board()
    assert robot._move_done_on_the_board == Move("e2e4")

    robot._currently_highlighted_squares = (Square("c6"), Square("c7"))
    with pytest.raises(
        NoNewMoveFoundOnTheChessboard, match="Something inconsistent happened"
    ):
        robot._recognize_move_done_on_the_board()
    assert robot._move_done_on_the_board is None


def test_perform_the_best_move_on_the_screen_and_internally():
    robot = get_robot()
    assert robot._our_last_move is None
    assert len(robot._chess_library.get_game_moves()) == 0

    move = Move("e2e4")
    robot._analysis.best_move = move
    robot._perform_the_best_move_on_the_screen_and_internally()
    assert len(robot._chess_library.get_game_moves()) == 1
    assert robot._chess_library.get_game_moves()[0] == move
    assert robot._our_last_move == move


@pytest.mark.timeout(1)
def test_perform_the_best_move_on_the_screen_and_internally_manual_trigger():
    robot = get_robot(trigger_moves_manually=True)
    assert robot._our_last_move is None
    assert len(robot._chess_library.get_game_moves()) == 0

    move = Move("e2e4")
    robot._analysis.best_move = move

    # First two should not trigger
    threading.Thread(target=sleep_and_press_key, args=("a", 1, 0.1)).start()
    threading.Thread(target=sleep_and_press_key, args=("b", 1, 0.2)).start()
    threading.Thread(target=sleep_and_press_key, args=("ctrlright", 1, 0.5)).start()

    start = time.perf_counter()
    robot._perform_the_best_move_on_the_screen_and_internally()
    assert len(robot._chess_library.get_game_moves()) == 1
    assert robot._chess_library.get_game_moves()[0] == move
    assert robot._our_last_move == move
    end = time.perf_counter()
    assert end - start > 0.5


def test_play_the_move_from_the_board_on_internal_board():
    robot = get_robot()
    assert robot._move_done_on_the_board is None
    assert len(robot._chess_library.get_game_moves()) == 0

    robot._play_the_move_from_the_board_on_internal_board()
    assert len(robot._chess_library.get_game_moves()) == 0

    robot._move_done_on_the_board = Move("e2e4")
    robot._play_the_move_from_the_board_on_internal_board()
    assert len(robot._chess_library.get_game_moves()) == 1
    assert robot._chess_library.get_game_moves()[0] == Move("e2e4")


def test_play_move_on_our_internal_board():
    robot = get_robot()
    assert robot._move_done_on_the_board is None
    assert len(robot._chess_library.get_game_moves()) == 0

    robot._play_move_on_our_internal_board(Move("e2e4"))
    assert len(robot._chess_library.get_game_moves()) == 1
    assert robot._chess_library.get_game_moves()[0] == Move("e2e4")


def test_analyze_position_and_suggest_the_best_move():
    robot = get_robot(observer_only_mode=True)
    original_analysis = robot._analysis
    robot._analyze_position_and_suggest_the_best_move()
    second_analysis = robot._analysis
    assert second_analysis != original_analysis
    robot._play_move_on_our_internal_board(Move("e2e4"))
    robot._analyze_position_and_suggest_the_best_move()
    third_analysis = robot._analysis
    assert third_analysis != original_analysis
    assert third_analysis != second_analysis


def test_get_time_to_think_according_to_last_position():
    robot = get_robot()

    robot._analysis.mate_string = "Mate in 3"
    assert robot._get_time_to_think_according_to_last_position() == 0.005
    robot._analysis.mate_string = None

    robot._analysis.pawn_score = -2.3
    assert robot._get_time_to_think_according_to_last_position() == 0.1

    robot._analysis.pawn_score = 0.4
    assert robot._get_time_to_think_according_to_last_position() == 0.01

    robot._analysis.pawn_score = 4.1
    assert robot._get_time_to_think_according_to_last_position() == 0.005


def test_format_move():
    robot = get_robot()
    assert robot._format_move(Move("e2e4")) == "e4"
    assert robot._format_move(Move("g1f3")) == "Nf3"

    with pytest.raises(ValueError, match="Invalid move"):
        robot._format_move(Move("b8c6"))
    robot._play_move_on_our_internal_board(Move("e2e4"))
    assert robot._format_move(Move("b8c6")) == "Nc6"


def test_check_if_the_game_did_not_finish():
    robot = get_robot()
    robot._check_if_the_game_did_not_finish()

    robot._play_move_on_our_internal_board(Move("f2f4"))
    robot._check_if_the_game_did_not_finish()
    robot._play_move_on_our_internal_board(Move("e7e6"))
    robot._check_if_the_game_did_not_finish()
    robot._play_move_on_our_internal_board(Move("g2g4"))
    robot._check_if_the_game_did_not_finish()
    robot._play_move_on_our_internal_board(Move("d8h4"))

    with pytest.raises(TheGameHasFinished, match="The game has finished"):
        robot._check_if_the_game_did_not_finish()


def test_evaluate_winner_and_finish_the_game(monkeypatch):
    robot = get_robot()

    with pytest.raises(ValueError, match="Game is not over"):
        robot._evaluate_winner_and_finish_the_game()

    monkeypatch.setattr(
        ChessLibrary,
        "get_game_outcome",
        lambda _x: ChessResult.Win,
    )
    with pytest.raises(TheGameHasFinished, match="You have won"):
        robot._evaluate_winner_and_finish_the_game()

    monkeypatch.setattr(
        ChessLibrary,
        "get_game_outcome",
        lambda _x: ChessResult.Lost,
    )
    with pytest.raises(TheGameHasFinished, match="You have lost"):
        robot._evaluate_winner_and_finish_the_game()

    monkeypatch.setattr(
        ChessLibrary,
        "get_game_outcome",
        lambda _x: ChessResult.Draw,
    )
    with pytest.raises(TheGameHasFinished, match="Draw"):
        robot._evaluate_winner_and_finish_the_game()


def test_look_at_the_chessboard_and_react_on_new_moves():
    robot = get_robot("black")
    img = Image.open(IMG / "lichess" / "black" / "0001.png")
    robot._look_at_the_chessboard_and_react_on_new_moves(img)
    assert robot._currently_highlighted_squares == (Square("e2"), Square("e4"))
    assert robot._move_done_on_the_board == Move("e2e4")
    assert robot._our_last_move == robot._best_move()
    assert robot._chess_library.get_game_moves() == [
        Move("e2e4"),
        robot._our_last_move,
    ]


def _test_whole_game(folder: Path, robot: ChessRobot, monkeypatch):
    all_screens = folder.glob("*.png")

    def mock_screenshot():
        return Image.open(next(all_screens))

    monkeypatch.setattr(
        src.chess_robot,
        "get_screenshot",
        mock_screenshot,
    )

    robot.start_the_game()

    game_file = folder / "game.pgn"
    game_moves = get_moves_from_game(game_file.read_text())
    assert game_moves == [
        move.raw_move for move in robot._chess_library.get_game_moves()
    ]
    assert robot._move_done_on_the_board == Move(game_moves[-1])
    assert robot._analysis.mate_string == "Mate in 1"


@pytest.mark.timeout(5)
def test_start_the_game_observe(monkeypatch, capfd):
    robot = get_robot("white", observer_only_mode=True)
    folder = IMG / "lichess" / "white_with_mate"
    _test_whole_game(folder, robot, monkeypatch)

    captured = capfd.readouterr()
    assert "Kicking the game by playing first" not in captured.out
    assert "ChessRobot debug info" not in captured.out
    assert "Taking debug screenshot" not in captured.out


@pytest.mark.timeout(5)
def test_start_the_game_observe_black(monkeypatch, capfd):
    robot = get_robot("black", observer_only_mode=True)
    folder = IMG / "lichess" / "black_with_mate"
    _test_whole_game(folder, robot, monkeypatch)

    captured = capfd.readouterr()
    assert "Kicking the game by playing first" not in captured.out
    assert "ChessRobot debug info" not in captured.out
    assert "Taking debug screenshot" not in captured.out


@pytest.mark.timeout(5)
def test_start_the_game_play_as_white(monkeypatch, capfd):
    robot = get_robot("white")
    folder = IMG / "lichess" / "white_with_mate"

    game_file = folder / "game.pgn"
    game_moves = get_moves_from_game(game_file.read_text())
    all_moves = (Move(move) for move in game_moves)

    def mock_best_move(self) -> Move:
        best_move = next(all_moves)
        # We must skip opponent moves, if there (missing at the end)
        try:
            _opponents_move = next(all_moves)
        except StopIteration:
            pass
        return best_move

    monkeypatch.setattr(
        ChessRobot,
        "_best_move",
        mock_best_move,
    )

    all_screens = folder.glob("*.png")

    def mock_screenshot():
        return Image.open(next(all_screens))

    monkeypatch.setattr(
        src.chess_robot,
        "get_screenshot",
        mock_screenshot,
    )

    robot.start_the_game()

    assert game_moves == [
        move.raw_move for move in robot._chess_library.get_game_moves()
    ]
    assert robot._move_done_on_the_board == Move(game_moves[-2])
    assert robot._analysis.mate_string == "Mate in 1"

    captured = capfd.readouterr()
    assert "Kicking the game by playing first" in captured.out
    assert "ChessRobot debug info" not in captured.out
    assert "Taking debug screenshot" not in captured.out


@pytest.mark.timeout(5)
def test_start_the_game_print_debug_info(monkeypatch, capfd):
    robot = get_robot("white")

    monkeypatch.setattr(
        src.chess_robot,
        "get_screenshot",
        lambda: 1 / 0,
    )

    with pytest.raises(ZeroDivisionError):
        robot.start_the_game()

    captured = capfd.readouterr()
    assert "Kicking the game by playing first" in captured.out
    assert "ChessRobot debug info" in captured.out
    assert "Taking debug screenshot" not in captured.out


@pytest.mark.timeout(10)
def test_start_the_game_observe_debug_mode(monkeypatch, capfd):
    monkeypatch.setattr(
        src.helpers,
        "save_screenshot_to_location",
        lambda _x: print("saving..."),
    )

    robot = get_robot("white", observer_only_mode=True, debug=True)
    folder = IMG / "lichess" / "white_with_mate"
    _test_whole_game(folder, robot, monkeypatch)

    captured = capfd.readouterr()
    assert "Kicking the game by playing first" not in captured.out
    assert "ChessRobot debug info" not in captured.out
    assert "Taking debug screenshot" in captured.out
