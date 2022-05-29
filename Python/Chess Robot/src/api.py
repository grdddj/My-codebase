"""
Defining interfaces for all the important components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Iterable, Protocol, Sequence

if TYPE_CHECKING:  # pragma: no cover
    from PIL import Image
    from pynput import keyboard

    from helpers import ColorValue, Pixel


@dataclass(frozen=True)
class Square:
    coordination: str

    def __post_init__(self):
        """Validating the square's correctness"""
        assert len(self.coordination) == 2, "Square must be 2 characters long"
        assert self.coordination[0] in "abcdefgh", "First coordinate must be a-h"
        assert self.coordination[1] in "12345678", "Second coordinate must be 1-8"

    def __add__(self, other: Square) -> Move:
        """Adding two Squares together creates a Move - from one Square to another"""
        assert isinstance(other, Square), "Can only add two Squares together"
        return Move(self.coordination + other.coordination)


@dataclass
class Move:
    raw_move: str
    from_square: Square = field(init=False)
    to_square: Square = field(init=False)
    promotion: str | None = field(init=False)

    def __post_init__(self):
        """Validating the move's correctness and calculating other fields"""
        assert len(self.raw_move) in (4, 5), "Move must have 4 or 5 characters"
        self.from_square = Square(self.raw_move[0:2])
        self.to_square = Square(self.raw_move[2:4])
        assert self.from_square != self.to_square, "Cannot move from a square to itself"
        if len(self.raw_move) == 5:
            assert self.to_square.coordination[1] in (
                "1",
                "8",
            ), "Can only promote on first/last row"
            self.promotion = self.raw_move[4].upper()
            assert (
                self.promotion in "QRBN"
            ), f"Invalid promotion piece {self.promotion} - QRBN are valid"
        else:
            self.promotion = None


class ChessResult(Enum):
    Win = 1
    Lost = 2
    Draw = 3


@dataclass
class AnalysisResult:
    pawn_score: float
    mate_string: str | None
    best_move: Move


class ChessboardAssignerInterface(Protocol):
    """Locates the chessboard on the screen"""

    def get_left_top_and_right_bottom_chessboard_pixels(
        self,
    ) -> tuple["Pixel", "Pixel"]:
        ...  # pragma: no cover


class ChessboardCoordinatesInterface(Protocol):
    """Holding information about chessboard fields"""

    def get_square_center(self, square: Square) -> "Pixel":
        ...  # pragma: no cover

    def get_all_square_items(self) -> Iterable[tuple[Square, "Pixel"]]:
        ...  # pragma: no cover

    def get_square_size(self) -> int:
        ...  # pragma: no cover


class ChessboardMonitoringInterface(Protocol):
    """Monitoring the chessboard on the screen"""

    def check_if_squares_are_highlighted(
        self, whole_screen: "Image.Image", squares_to_check: Sequence[Square]
    ) -> bool:
        ...  # pragma: no cover

    def get_highlighted_squares(self, whole_screen: "Image.Image") -> list[Square]:
        ...  # pragma: no cover


class ChessboardPlayingInterface(Protocol):
    """Playing the moves on the screen"""

    def play_move(self, move: Move) -> None:
        ...  # pragma: no cover


class ChessLibraryInterface(Protocol):
    """Keeps track of the position on the chessboard and suggests best moves"""

    def should_start_as_white(self) -> bool:
        ...  # pragma: no cover

    def is_valid_move(self, move: Move) -> bool:
        ...  # pragma: no cover

    def play_move(self, move: Move) -> None:
        ...  # pragma: no cover

    def get_current_analysis_result(self, time_to_think: float) -> AnalysisResult:
        ...  # pragma: no cover

    def is_game_over(self) -> bool:
        ...  # pragma: no cover

    def get_game_outcome(self) -> ChessResult:
        ...  # pragma: no cover

    def get_notation_from_move(self, move: Move) -> str:
        ...  # pragma: no cover


class ConfigInterface(Protocol):
    observer_only_mode: bool
    force_boundaries_update: bool
    trigger_moves_manually: bool
    website: str
    mode: str
    debug: bool

    engine_location: str

    time_limit_to_think_normal: float
    time_limit_to_think_when_already_winning: float
    time_limit_to_think_when_losing: float

    pawn_threshold_when_already_winning: float
    pawn_threshold_when_losing: float

    should_sleep: bool
    sleep_interval_between_screenshots: float

    keyboard_trigger: "keyboard.Key"

    chessboard_left_top_pixel: "Pixel"
    chessboard_right_bottom_pixel: "Pixel"
    white_field_highlight_colour: "ColorValue"
    black_field_highlight_colour: "ColorValue"
