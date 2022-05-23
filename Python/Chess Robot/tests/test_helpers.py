import threading
import time
from pathlib import Path

import pyautogui
from PIL import Image

from src.helpers import (
    are_there_colours_in_a_PIL_image,
    check_for_option_in_cmdline,
    get_piece_colour,
    save_new_boundaries_into_config,
)

HERE = Path(__file__).resolve().parent


def _sleep_and_press_key(
    key: str,
    amount: int = 2,
    sleep_time: float = 0.5,
) -> None:
    time.sleep(sleep_time)
    for _ in range(amount):
        pyautogui.press(key)


def test_check_for_option_in_cmdline(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "abc", "foo", "ber"])

    assert check_for_option_in_cmdline(("foo", "bar", "baz"), "def") == "foo"
    assert check_for_option_in_cmdline(("roo", "bar", "baz"), "def") == "def"


def test_get_piece_colour():
    threading.Thread(target=_sleep_and_press_key, args=("b", 2, 0.1)).start()
    assert get_piece_colour() == "black"

    threading.Thread(target=_sleep_and_press_key, args=("w", 2, 0.1)).start()
    assert get_piece_colour() == "white"

    # any other key than "b" gives white as well
    threading.Thread(target=_sleep_and_press_key, args=("x", 2, 0.1)).start()
    assert get_piece_colour() == "white"


def test_are_there_colours_in_a_PIL_image():
    img_location = HERE / "img" / "rainbow.jpg"
    img = Image.open(img_location)

    # are there
    red = (254, 0, 0)
    green = (1, 204, 0)
    blue = (0, 0, 204)

    # are not there
    black = (0, 0, 0)
    white = (255, 255, 255)

    assert not are_there_colours_in_a_PIL_image(img, (black,))
    assert not are_there_colours_in_a_PIL_image(img, (black, white))
    assert are_there_colours_in_a_PIL_image(img, (red,))
    assert are_there_colours_in_a_PIL_image(img, (green,))
    assert are_there_colours_in_a_PIL_image(img, (blue,))
    assert are_there_colours_in_a_PIL_image(img, (red, green, blue, black, white))
    assert are_there_colours_in_a_PIL_image(img, (red, white))


def test_save_new_boundaries_into_config(tmp_path):
    config_file = tmp_path / "config.py"

    original_content = """\
    ###########################################
    # PART ABOUT THE COORDINATES AND COLOURS - website dependent
    ###########################################

    if self.website == "lichess":
        self.chessboard_left_top_pixel = (541, 225)
        self.chessboard_right_bottom_pixel = (1164, 854)
    elif self.website == "chess.com":
        self.chessboard_left_top_pixel = (334, 272)
        self.chessboard_right_bottom_pixel = (966, 903)
        # self.chessboard_left_top_pixel = (334, 272)
        # self.chessboard_right_bottom_pixel = (966, 903)
    elif self.website == "kurnik":
        # https://www.playok.com/cs/sachy/
        self.chessboard_left_top_pixel = (341, 205)
        self.chessboard_right_bottom_pixel = (1107, 970)
    else:
        raise ValueError(f"Unknown website: {self.website}")
"""

    config_file.write_text(original_content)

    save_new_boundaries_into_config(
        (111, 111), (666, 666), "chess.com", file_name=config_file
    )

    new_content = """\
    ###########################################
    # PART ABOUT THE COORDINATES AND COLOURS - website dependent
    ###########################################

    if self.website == "lichess":
        self.chessboard_left_top_pixel = (541, 225)
        self.chessboard_right_bottom_pixel = (1164, 854)
    elif self.website == "chess.com":
        self.chessboard_left_top_pixel = (111, 111)
        self.chessboard_right_bottom_pixel = (666, 666)
        # self.chessboard_left_top_pixel = (334, 272)
        # self.chessboard_right_bottom_pixel = (966, 903)
    elif self.website == "kurnik":
        # https://www.playok.com/cs/sachy/
        self.chessboard_left_top_pixel = (341, 205)
        self.chessboard_right_bottom_pixel = (1107, 970)
    else:
        raise ValueError(f"Unknown website: {self.website}")
"""

    assert config_file.read_text() == new_content
