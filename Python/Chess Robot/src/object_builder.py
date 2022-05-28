"""
Component for dependency injection.

Creating objects based on the user input.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from .chess_library import ChessLibrary
from .chess_robot import ChessRobot
from .chessboard_assigner import ChessboardAssigner
from .chessboard_coordinates import ChessboardCoordinates
from .chessboard_monitor import ChessboardMonitor, ChessboardMonitorKurnik
from .chessboard_player import ChessboardPlayer
from .config import Config
from .helpers import check_for_option_in_cmdline, save_new_boundaries_into_config

if TYPE_CHECKING:  # pragma: no cover
    from .helpers import PieceColour


def get_robot(config: "Config", our_piece_colour: "PieceColour") -> ChessRobot:
    chessboard_coordinates = ChessboardCoordinates(
        left_top=config.chessboard_left_top_pixel,
        right_bottom=config.chessboard_right_bottom_pixel,
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


def get_config() -> "Config":
    observer_only_mode = _observer_only_mode()
    if observer_only_mode:
        print("Observer mode - not playing the moves")

    force_boundaries_update = _force_boundaries_update()
    if force_boundaries_update:
        print("Forcing the boundaries update")

    trigger_moves_manually = _trigger_moves_manually()
    if trigger_moves_manually:
        print("Will wait with moves for the trigger")

    website = _website()
    mode = _mode()
    debug = _debug()

    if debug:
        print("Debug mode - will be saving all the unique screenshots")

    print(f"Loading config for website {website}, mode {mode}")

    config = Config(
        observer_only_mode=observer_only_mode,
        force_boundaries_update=force_boundaries_update,
        trigger_moves_manually=trigger_moves_manually,
        website=website,
        mode=mode,
        debug=debug,
    )

    # Boundaries may, or may not be defined in config - and update can be forced
    if (
        config.force_boundaries_update
        or config.chessboard_left_top_pixel is None
        or config.chessboard_right_bottom_pixel is None
    ):
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

        config.chessboard_left_top_pixel = left_top
        config.chessboard_right_bottom_pixel = right_bottom

    return config


def _observer_only_mode() -> bool:
    return "observe" in sys.argv


def _force_boundaries_update() -> bool:
    return "force" in sys.argv


def _trigger_moves_manually() -> bool:
    return "trigger" in sys.argv


def _debug() -> bool:
    return "debug" in sys.argv


def _mode() -> str:
    return check_for_option_in_cmdline(
        ("superblitz", "blitz", "slow"), default="superblitz"
    )


def _website() -> str:
    return check_for_option_in_cmdline(
        ("lichess", "chess.com", "kurnik"), default="lichess"
    )
