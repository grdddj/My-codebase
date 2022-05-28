import io
import time

import chess
import chess.pgn
import pyautogui

pyautogui.PAUSE = 0.01


def sleep_and_press_key(
    key: str,
    amount: int = 2,
    sleep_time: float = 0.5,
) -> None:
    time.sleep(sleep_time)
    for _ in range(amount):
        pyautogui.press(key)


def sleep_and_click_at_coordinates(
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


def get_moves_from_game(pgn_game: str) -> list[str]:
    game = chess.pgn.read_game(io.StringIO(pgn_game))
    assert game is not None
    return [str(move) for move in game.mainline_moves()]
