import threading
import time

import pyautogui

from src.chessboard_assigner import ChessboardAssigner


def _sleep_and_click_at_coordinates(
    coords: tuple[int, int],
    button: str = "left",
    sleep_time: float = 0.5,
) -> None:
    # So we can return the cursor back where we started
    initial_cursor_position = pyautogui.position()

    time.sleep(sleep_time)
    pyautogui.click(*coords, button=button)

    pyautogui.moveTo(*initial_cursor_position)
    pyautogui.click(*initial_cursor_position)


def test_assign_chessboard():
    assigner = ChessboardAssigner()

    def _assign_both_corners() -> None:
        _sleep_and_click_at_coordinates((300, 300), "right", 0.1)
        _sleep_and_click_at_coordinates((900, 900), "right", 0.1)

    threading.Thread(target=_assign_both_corners).start()

    results = assigner.get_left_top_and_right_bottom_chessboard_pixels()
    assert results == ((300, 300), (900, 900))
