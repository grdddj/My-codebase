# Documentation here: https://python-chess.readthedocs.io/en/latest/
from typing import TYPE_CHECKING

import chess
import chess.engine

from .api import AnalysisResult, ChessLibraryInterface, ChessResult, Move

if TYPE_CHECKING:
    from .helpers import PieceColour


class ChessLibrary(ChessLibraryInterface):
    def __init__(self, our_piece_colour: "PieceColour", engine_location: str) -> None:
        self.our_color = chess.WHITE if our_piece_colour == "white" else chess.BLACK
        self.board = chess.Board()
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_location)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find engine at {engine_location}. Make sure the path is correct."
            ) from None

    def should_start_as_white(self) -> bool:
        return self.our_color == chess.WHITE and self.board.fullmove_number == 1

    def is_valid_move(self, move: Move) -> bool:
        return chess.Move.from_uci(move.raw_move) in self.board.legal_moves

    def play_move(self, move: Move) -> None:
        self.board.push(chess.Move.from_uci(move.raw_move))

    def get_current_analysis_result(self, time_to_think: float) -> AnalysisResult:
        result = self.engine.analyse(
            board=self.board, limit=chess.engine.Limit(time=time_to_think)
        )

        assert "score" in result
        score_from_our_side = str(result["score"].pov(self.our_color))

        if result["score"].is_mate():
            pawn_score = float("inf")
            mate_string = score_from_our_side
        else:
            pawn_score = int(score_from_our_side) / 100
            mate_string = None

        assert "pv" in result
        best_move = Move(str(result["pv"][0]))

        return AnalysisResult(
            pawn_score=pawn_score, mate_string=mate_string, best_move=best_move
        )

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def get_game_outcome(self) -> ChessResult:
        outcome = self.board.outcome()
        assert outcome is not None

        if outcome.winner == chess.WHITE:
            return (
                ChessResult.Win if self.our_color == chess.WHITE else ChessResult.Lost
            )
        elif outcome.winner == chess.BLACK:
            return (
                ChessResult.Win if self.our_color == chess.BLACK else ChessResult.Lost
            )
        else:
            return ChessResult.Draw

    def get_notation_from_move(self, move: Move) -> str:
        return self.board.san(chess.Move.from_uci(move.raw_move))