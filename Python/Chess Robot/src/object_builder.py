"""
Component for dependency injection.

Creating objects based on the user input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .chess_library import ChessLibrary
from .chess_robot import ChessRobot
from .chessboard_assigner import ChessboardAssigner
from .chessboard_coordinates import ChessboardCoordinates
from .chessboard_monitor import ChessboardMonitor, ChessboardMonitorKurnik
from .chessboard_player import ChessboardPlayer
from .helpers import save_new_boundaries_into_config

if TYPE_CHECKING:
    from .config import Config
    from .helpers import PieceColour, Pixel


def get_robot(config: "Config", our_piece_colour: "PieceColour") -> ChessRobot:
    boundaries = _get_boundaries_cached(config)

    chessboard_coordinates = ChessboardCoordinates(
        left_top=boundaries[0],
        right_bottom=boundaries[1],
        our_piece_colour=our_piece_colour,
    )

    # Kurnik website has a special handler
    monitor_class = (
        ChessboardMonitorKurnik if config.website == "kurnik" else ChessboardMonitor
    )
    chessboard_monitor = monitor_class(
        chessboard_coordinates=chessboard_coordinates,
        highlighted_colours=[
            config.white_field_highlight_colour,
            config.black_field_highlight_colour,
        ],
    )

    chessboard_player = ChessboardPlayer(chessboard_coordinates)

    chess_library = ChessLibrary(our_piece_colour, config.engine_location)

    return ChessRobot(
        chessboard_monitor=chessboard_monitor,
        chessboard_player=chessboard_player,
        chess_library=chess_library,
        config=config,
    )


# Caching so it is needed only at the first time
LEFT_TOP: "Pixel" | None = None
BOTTOM_RIGHT: "Pixel" | None = None


def _get_boundaries_cached(config: "Config") -> tuple["Pixel", "Pixel"]:
    global LEFT_TOP, BOTTOM_RIGHT

    if LEFT_TOP is None and BOTTOM_RIGHT is None:
        LEFT_TOP, BOTTOM_RIGHT = _get_boundaries(config)

    assert LEFT_TOP is not None and BOTTOM_RIGHT is not None
    return LEFT_TOP, BOTTOM_RIGHT


def _get_boundaries(config: "Config") -> tuple["Pixel", "Pixel"]:
    left_top = config.chessboard_left_top_pixel
    right_bottom = config.chessboard_right_bottom_pixel

    # Boundaries may, or may not be defined in config - and update can be forced
    if config.force_boundaries_update or left_top is None or right_bottom is None:
        chessboard_assigner = ChessboardAssigner()
        boundaries = (
            chessboard_assigner.get_left_top_and_right_bottom_chessboard_pixels()
        )
        left_top = boundaries[0]
        right_bottom = boundaries[1]

        save_new_boundaries_into_config(
            left_top,
            right_bottom,
            website=config.website,
        )

    return left_top, right_bottom
