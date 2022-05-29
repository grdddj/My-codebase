import threading

import pytest

from src.chessboard_assigner import ChessboardAssigner

from .helpers import sleep_and_click_at_coordinates


@pytest.mark.timeout(1)
def test_assign_chessboard():
    assigner = ChessboardAssigner()

    def _assign_both_corners() -> None:
        sleep_and_click_at_coordinates((300, 300), "right", 0.1)
        sleep_and_click_at_coordinates((900, 900), "right", 0.1)

    threading.Thread(target=_assign_both_corners).start()

    results = assigner.get_left_top_and_right_bottom_chessboard_pixels()
    assert results == ((300, 300), (900, 900))
