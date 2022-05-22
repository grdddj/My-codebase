from typing import TYPE_CHECKING, Iterable

from api import ChessboardCoordinatesInterface, Square

if TYPE_CHECKING:
    from helpers import PieceColour, Pixel


class ChessboardCoordinates(ChessboardCoordinatesInterface):
    def __init__(
        self, left_top: "Pixel", right_bottom: "Pixel", our_piece_colour: "PieceColour"
    ):
        self.square_size = (right_bottom[0] - left_top[0]) // 8
        assert self.square_size > 0, "mismatch in coordinates"
        self.square_centers_dict = self._create_dict_of_square_centers(
            left_top, right_bottom, our_piece_colour
        )

    def get_square_center(self, square: Square) -> "Pixel":
        if square not in self.square_centers_dict:
            raise ValueError(f"{square} is not a valid square!")

        return self.square_centers_dict[square]

    def get_all_square_items(self) -> Iterable[tuple[Square, "Pixel"]]:
        return self.square_centers_dict.items()

    def get_square_size(self) -> int:
        return self.square_size

    @staticmethod
    def _create_dict_of_square_centers(
        left_top: "Pixel",
        right_bottom: "Pixel",
        our_piece_colour: "PieceColour",
    ) -> dict[Square, "Pixel"]:
        chessboard_size = right_bottom[0] - left_top[0]
        square_size = chessboard_size // 8

        # Constructing the dictionary of square centers
        # We must distinguish between playing white or black when doing that
        rows = "12345678"
        columns = "abcdefgh"
        square_centers_dict: dict[Square, "Pixel"] = {}

        for col_index, col in enumerate(columns):
            for row_index, row in enumerate(rows):
                if our_piece_colour == "white":
                    center_x = left_top[0] + (
                        square_size // 2 + col_index * square_size
                    )
                    center_y = right_bottom[1] - (
                        square_size // 2 + row_index * square_size
                    )
                else:
                    center_x = right_bottom[0] - (
                        square_size // 2 + col_index * square_size
                    )
                    center_y = left_top[1] + (
                        square_size // 2 + row_index * square_size
                    )

                square = Square(col + row)
                square_centers_dict[square] = (center_x, center_y)

        return square_centers_dict
