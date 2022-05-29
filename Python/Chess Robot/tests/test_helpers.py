import threading
import time
from pathlib import Path

import pytest
from PIL import Image

from src.helpers import (
    are_there_colours_in_a_PIL_image,
    check_for_option_in_cmdline,
    get_piece_colour,
    get_screenshot,
    save_new_boundaries_into_config,
    save_screenshot,
    wait_to_trigger_the_game,
)

from .helpers import get_moves_from_game, sleep_and_press_key

HERE = Path(__file__).resolve().parent


def test_check_for_option_in_cmdline(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "abc", "foo", "ber"])

    assert check_for_option_in_cmdline(("foo", "bar", "baz"), "def") == "foo"
    assert check_for_option_in_cmdline(("roo", "bar", "baz"), "def") == "def"


@pytest.mark.timeout(1)
def test_wait_to_trigger_the_game():
    start = time.perf_counter()
    # First two should not trigger
    threading.Thread(target=sleep_and_press_key, args=("a", 1, 0.1)).start()
    threading.Thread(target=sleep_and_press_key, args=("b", 1, 0.2)).start()
    threading.Thread(target=sleep_and_press_key, args=("ctrlright", 1, 0.5)).start()
    wait_to_trigger_the_game()
    end = time.perf_counter()
    assert end - start > 0.5


@pytest.mark.timeout(1)
def test_get_piece_colour():
    threading.Thread(target=sleep_and_press_key, args=("b", 2, 0.1)).start()
    assert get_piece_colour() == "black"

    threading.Thread(target=sleep_and_press_key, args=("w", 2, 0.1)).start()
    assert get_piece_colour() == "white"

    # any other key than "b" gives white as well
    threading.Thread(target=sleep_and_press_key, args=("x", 2, 0.1)).start()
    assert get_piece_colour() == "white"


def test_get_screenshot():
    screenshot = get_screenshot()
    assert isinstance(screenshot, Image.Image)


def test_save_screenshot():
    screenshot = save_screenshot()
    assert Path(screenshot).exists()
    Path(screenshot).unlink()
    assert not Path(screenshot).exists()


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
    red_almost = (255, 0, 0)

    assert not are_there_colours_in_a_PIL_image(img, (black,))
    assert not are_there_colours_in_a_PIL_image(img, (black, white))
    assert not are_there_colours_in_a_PIL_image(img, (red_almost,))
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


def test_get_moves_from_game():
    game = "1. d4 Nf6 2. c4 e6 3. Nc3 Be7 4. e4 O-O"
    moves = get_moves_from_game(game)
    assert moves == ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8e7", "e2e4", "e8g8"]

    game = "1. d3 c6 2. Bf4 b6 3. Nc3 d6 4. Qd2 Nd7 5. O-O-O"
    moves = get_moves_from_game(game)
    assert moves == [
        "d2d3",
        "c7c6",
        "c1f4",
        "b7b6",
        "b1c3",
        "d7d6",
        "d1d2",
        "b8d7",
        "e1c1",
    ]
