from pathlib import Path
from typing import Literal

import pytest

from src.api import ChessResult, Move
from src.chess_library import ChessLibrary

from .helpers import get_moves_from_game

HERE = Path(__file__).resolve().parent
ROOT_DIR = HERE.parent

DEFAULT_ENGINE = ROOT_DIR / "engines" / "stockfish_15_x64_bmi2"


def get_chess(
    colour: Literal["white", "black"], engine: Path = DEFAULT_ENGINE
) -> ChessLibrary:
    return ChessLibrary(
        our_piece_colour=colour,
        engine_location=str(engine),
    )


def test_invalid_colour():
    with pytest.raises(AssertionError, match="Invalid piece colour"):
        get_chess("blackandwhite")  # type: ignore


def test_unexisting_engine():
    with pytest.raises(FileNotFoundError, match="Could not find engine"):
        get_chess("white", ROOT_DIR / "engines" / "unexisting_stockfish")


def test_should_start_as_white():
    chess = get_chess("white")
    assert chess.should_start_as_white()

    chess = get_chess("black")
    assert not chess.should_start_as_white()


def test_is_valid_move():
    chess = get_chess("white")
    assert chess.is_valid_move(Move("e2e4"))
    assert chess.is_valid_move(Move("b1c3"))
    assert not chess.is_valid_move(Move("e2e5"))
    assert not chess.is_valid_move(Move("e7e5"))

    chess.play_move(Move("e2e4"))
    assert not chess.is_valid_move(Move("e2e4"))
    assert chess.is_valid_move(Move("e7e5"))
    assert chess.is_valid_move(Move("g8f6"))


def test_is_valid_move_whole_game():
    chess = get_chess("white")
    png_game = "1. e4 c6 2. d4 d5 3. e5 Bf5 4. Be2 e6 5. Nf3 c5 6. O-O cxd4 7. Nxd4 Bg6 8. h4 Qc7 9. h5 Nc6 10. Nxc6 Qxc6 11. hxg6 fxg6 12. Nd2 Be7 13. c4 d4 14. Bf3 Qc7 15. Qa4+ Kd8 16. Ne4 Nh6 17. c5 Nf5 18. Nd6 Bf6 19. Nxb7+ Qxb7 20. Bxb7 Ne3 21. Qa5+ Ke7 22. Qc7+ Kf8 23. fxe3 Kg8 24. Bxa8 dxe3 25. exf6 e5 26. Qxg7#"
    game = get_moves_from_game(png_game)
    for move in game:
        assert chess.is_valid_move(Move(move))
        chess.play_move(Move(move))


def test_play_move():
    chess = get_chess("white")
    assert chess._board.fullmove_number == 1

    chess.play_move(Move("e2e4"))
    assert chess._board.fullmove_number == 1

    chess.play_move(Move("e7e5"))
    assert chess._board.fullmove_number == 2


def test_is_game_over():
    chess = get_chess("white")
    chess.play_move(Move("f2f4"))
    chess.play_move(Move("e7e6"))
    chess.play_move(Move("g2g4"))
    assert not chess.is_game_over()

    chess.play_move(Move("d8h4"))
    assert chess.is_game_over()


def test_get_game_outcome():
    chess = get_chess("white")
    with pytest.raises(AssertionError, match="Game is not over"):
        chess.get_game_outcome()

    chess = get_chess("white")
    chess.play_move(Move("f2f4"))
    chess.play_move(Move("e7e6"))
    chess.play_move(Move("g2g4"))
    chess.play_move(Move("d8h4"))
    assert chess.get_game_outcome() == ChessResult.Lost

    chess = get_chess("white")
    chess.play_move(Move("e2e4"))
    chess.play_move(Move("f7f6"))
    chess.play_move(Move("f1e2"))
    chess.play_move(Move("g7g5"))
    chess.play_move(Move("e2h5"))
    assert chess.get_game_outcome() == ChessResult.Win

    chess = get_chess("black")
    chess.play_move(Move("f2f4"))
    chess.play_move(Move("e7e6"))
    chess.play_move(Move("g2g4"))
    chess.play_move(Move("d8h4"))
    assert chess.get_game_outcome() == ChessResult.Win

    chess = get_chess("white")
    stalemate_game_png = "1.e3 a5 2.Qh5 Ra6 3.Qxa5 h5 4.Qxc7 Rah6 5.h4 f6 6.Qxd7+ Kf7 7.Qxb7 Qd3 8.Qxb8 Qh7 9.Qxc8 Kg6 10.Qe6"
    game = get_moves_from_game(stalemate_game_png)
    for move in game:
        chess.play_move(Move(move))
    assert chess.get_game_outcome() == ChessResult.Draw


def test_get_notation_from_move():
    chess = get_chess("white")
    assert chess.get_notation_from_move(Move("e2e4")) == "e4"
    chess.play_move(Move("e2e4"))
    assert chess.get_notation_from_move(Move("g8f6")) == "Nf6"


def test_get_current_analysis_result():
    chess = get_chess("black")
    chess.play_move(Move("f2f4"))
    analysis = chess.get_current_analysis_result(0.01)
    assert -1 < analysis.pawn_score < 1
    assert analysis.mate_string is None

    chess.play_move(Move("e7e6"))
    chess.play_move(Move("g2g4"))
    analysis = chess.get_current_analysis_result(0.01)
    assert analysis.best_move == Move("d8h4")
    assert analysis.pawn_score > 10
    assert analysis.mate_string == "Mate in 1"
