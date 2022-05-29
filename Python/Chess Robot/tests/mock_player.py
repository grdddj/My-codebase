from src.api import ChessboardCoordinatesInterface, ChessboardPlayingInterface, Move


class MockPlayer(ChessboardPlayingInterface):
    def __init__(
        self, chessboard_coordinates: "ChessboardCoordinatesInterface"
    ) -> None:
        pass

    def play_move(self, move: "Move") -> None:
        print("Playing move:", move)
