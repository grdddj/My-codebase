import time
from typing import TYPE_CHECKING

import pyautogui

from .api import ChessboardPlayingInterface
from .helpers import move_mouse_back

if TYPE_CHECKING:  # pragma: no cover
    from .api import ChessboardCoordinatesInterface, Move, Square

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.0001


class ChessboardPlayer(ChessboardPlayingInterface):
    def __init__(
        self, chessboard_coordinates: "ChessboardCoordinatesInterface"
    ) -> None:
        self._chessboard_coordinates = chessboard_coordinates

    def play_move(self, move: "Move") -> None:
        with move_mouse_back():
            self._click_on_square(move.from_square)
            self._click_on_square(move.to_square)

            # If there is a promotion, presume we will have a queen, so click
            #   the to_square once again
            if move.promotion is not None:
                time.sleep(0.5)  # need to wait for the promotion dialogue
                # TODO: account for a specific piece (queen, rook, bishop, knight)
                self._click_on_square(move.to_square)

    def _click_on_square(self, square: "Square") -> None:
        pyautogui.click(*self._chessboard_coordinates.get_square_center(square))
