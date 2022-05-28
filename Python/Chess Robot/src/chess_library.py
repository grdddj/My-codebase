# Documentation here: https://python-chess.readthedocs.io/en/latest/
from typing import TYPE_CHECKING

import chess
import chess.engine

from .api import AnalysisResult, ChessLibraryInterface, ChessResult, Move

if TYPE_CHECKING:  # pragma: no cover
    from .helpers import PieceColour


class ChessLibrary(ChessLibraryInterface):
    def __init__(self, our_piece_colour: "PieceColour", engine_location: str) -> None:
        assert our_piece_colour in ("white", "black"), "Invalid piece colour"
        self._our_color = chess.WHITE if our_piece_colour == "white" else chess.BLACK
        self._board = chess.Board()
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(engine_location)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find engine at {engine_location}. Make sure the path is correct."
            ) from None

    def should_start_as_white(self) -> bool:
        return self._our_color == chess.WHITE and self._board.fullmove_number == 1

    def is_valid_move(self, move: Move) -> bool:
        return chess.Move.from_uci(move.raw_move) in self._board.legal_moves

    def play_move(self, move: Move) -> None:
        self._board.push(chess.Move.from_uci(move.raw_move))

    def get_current_analysis_result(self, time_to_think: float) -> AnalysisResult:
        result = self._engine.analyse(
            board=self._board, limit=chess.engine.Limit(time=time_to_think)
        )

        assert "score" in result
        score_from_our_side = str(result["score"].pov(self._our_color))

        if result["score"].is_mate():
            pawn_score = float("inf")
            mate_string = f"Mate in {score_from_our_side.split('+')[1]}"
        else:
            pawn_score = int(score_from_our_side) / 100
            mate_string = None

        assert "pv" in result
        best_move = Move(str(result["pv"][0]))

        return AnalysisResult(
            pawn_score=pawn_score, mate_string=mate_string, best_move=best_move
        )

    def is_game_over(self) -> bool:
        return self._board.is_game_over()

    def get_game_outcome(self) -> ChessResult:
        outcome = self._board.outcome()
        assert outcome is not None, "Game is not over"

        if outcome.winner == chess.WHITE:
            return (
                ChessResult.Win if self._our_color == chess.WHITE else ChessResult.Lost
            )
        elif outcome.winner == chess.BLACK:
            return (
                ChessResult.Win if self._our_color == chess.BLACK else ChessResult.Lost
            )
        else:
            return ChessResult.Draw

    def get_notation_from_move(self, move: Move) -> str:
        return self._board.san(chess.Move.from_uci(move.raw_move))
