import time
from typing import TYPE_CHECKING

import pyautogui

from .api import ChessboardPlayingInterface

if TYPE_CHECKING:
    from .api import ChessboardCoordinatesInterface, Move, Square

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.0001


class ChessboardPlayer(ChessboardPlayingInterface):
    def __init__(
        self, chessboard_coordinates: "ChessboardCoordinatesInterface"
    ) -> None:
        self.chessboard_coordinates = chessboard_coordinates

    def play_move(self, move: "Move") -> None:
        # So we can return the cursor back where we started
        initial_cursor_position = pyautogui.position()

        self._click_on_square(move.from_square)
        self._click_on_square(move.to_square)

        # If there is a promotion, presume we will have a queen, so click
        #   the to_square once again
        if move.promotion:
            time.sleep(0.5)  # need to wait for the promotion dialogue
            self._click_on_square(move.to_square)

        pyautogui.moveTo(*initial_cursor_position)
        pyautogui.click(*initial_cursor_position)

    def _click_on_square(self, square: "Square") -> None:
        pyautogui.click(*self.chessboard_coordinates.get_square_center(square))
