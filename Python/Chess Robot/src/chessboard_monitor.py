from typing import TYPE_CHECKING, Sequence

import pyautogui
from PIL import Image

from .api import ChessboardMonitoringInterface, Square
from .helpers import are_there_colours_in_a_PIL_image

if TYPE_CHECKING:  # pragma: no cover
    from .api import ChessboardCoordinatesInterface
    from .helpers import ColorValue

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.0001


class ChessboardMonitor(ChessboardMonitoringInterface):
    def __init__(
        self,
        chessboard_coordinates: "ChessboardCoordinatesInterface",
        highlighted_colours: list["ColorValue"],
    ) -> None:
        self._chessboard_coordinates = chessboard_coordinates
        self._highlighted_colours = highlighted_colours

    def get_highlighted_squares(self, whole_screen: Image.Image) -> list[Square]:
        highlighted_squares: list[Square] = []

        # Looping through all squares, and testing if they contain highlighted colour
        for square, _ in self._chessboard_coordinates.get_all_square_items():
            if self._square_is_highlighted(whole_screen, square):
                highlighted_squares.append(square)

            # Exiting when we have found two squares, there should not be more
            if len(highlighted_squares) == 2:
                break

        return highlighted_squares

    def check_if_squares_are_highlighted(
        self, whole_screen: Image.Image, squares_to_check: Sequence[Square]
    ) -> bool:
        return all(
            self._square_is_highlighted(whole_screen, square)
            for square in squares_to_check
        )

    def _square_is_highlighted(
        self, whole_screen: Image.Image, square: "Square"
    ) -> bool:
        square_center_coords = self._chessboard_coordinates.get_square_center(square)
        square_size = self._chessboard_coordinates.get_square_size()

        # Defining how big part of a square will be cut out to allow for some
        #   inaccuracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0.2
        square_boundary_pixels = int(square_size * square_boundary)

        left_top_x_square = square_center_coords[0] - square_size // 2
        left_top_y_square = square_center_coords[1] - square_size // 2
        corners_of_current_square = (
            left_top_x_square + square_boundary_pixels,
            left_top_y_square + square_boundary_pixels,
            left_top_x_square + square_size - square_boundary_pixels,
            left_top_y_square + square_size - square_boundary_pixels,
        )
        square_image = whole_screen.crop(corners_of_current_square)

        return are_there_colours_in_a_PIL_image(square_image, self._highlighted_colours)


class ChessboardMonitorKurnik(ChessboardMonitor):
    """Special handler for Kurnik chessboard, where highlighting works differently.

    Instead of the whole square being highlighted by a special colour,
    here just the special colour is just on the edges.
    """

    def _square_is_highlighted(
        self, whole_screen: Image.Image, square: "Square"
    ) -> bool:
        square_center_coords = self._chessboard_coordinates.get_square_center(square)
        square_size = self._chessboard_coordinates.get_square_size()

        left_top_x_square = square_center_coords[0] - square_size // 2
        left_top_y_square = square_center_coords[1] - square_size // 2
        corners_of_current_square = (
            left_top_x_square,
            left_top_y_square,
            left_top_x_square + square_size,
            left_top_y_square + square_size,
        )
        square_image = whole_screen.crop(corners_of_current_square)

        # Creating four sub-squares, to test if the colour is present in
        #   at least three of them - which signs success
        length = square_image.size[0]
        step = length // 2
        sub_squares_corners = [
            (0, 0, step, step),
            (step, 0, step * 2, step),
            (0, step, step, step * 2),
            (step, step, step * 2, step * 2),
        ]

        found_in_corner = 0
        for smaller_square_corner in sub_squares_corners:
            if are_there_colours_in_a_PIL_image(
                square_image.crop(smaller_square_corner),
                self._highlighted_colours,
            ):
                found_in_corner += 1

        return found_in_corner > 2
