from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Sequence

import pyautogui
from PIL import Image
from pynput import keyboard

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.0001

if TYPE_CHECKING:  # pragma: no cover
    Pixel = tuple[int, int]
    ColorValue = tuple[int, int, int]
    PieceColour = Literal["white", "black"]


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def check_for_option_in_cmdline(possible_options: Sequence[str], default: str) -> str:
    """Looks for certain options in the command line and returns the first one found"""
    for option in possible_options:
        if option in sys.argv:
            return option

    return default


def get_piece_colour() -> "PieceColour":
    """Ask user to choose the colour of the pieces - black/white"""
    press_amount = 2
    print(
        f"Choose your piece colour. For white, press 'w' {press_amount} times. For black, press 'b' {press_amount} times."
    )
    double_pressed_key = get_more_pressed_key(press_amount)
    if str(double_pressed_key).strip("'").lower() == "b":
        our_piece_colour: "PieceColour" = "black"
    else:
        our_piece_colour = "white"

    print(f"You chose {our_piece_colour} pieces, good luck in the game!")

    return our_piece_colour


def get_screenshot() -> Image.Image:
    """Return the current screen - only the main monitor is covered"""
    return pyautogui.screenshot()


def save_screenshot() -> str:
    """Saves the current screen as a screenshot into our folder"""
    time.sleep(0.1)  # wait for screen to stabilize
    folder = ROOT / "screens"
    file_amount = len(list(folder.glob("*.png")))
    location = ROOT / "screens" / f"screenshot_{file_amount:04}.png"
    print("Taking debug screenshot", location)
    save_screenshot_to_location(location)
    return str(location)


def save_screenshot_to_location(location: str | Path) -> None:
    """Saves the current screen as a screenshot into specified place"""
    pyautogui.screenshot(location)


def wait_to_trigger_the_game() -> None:
    """Wait for user to press a key to start the game"""
    print("Press right Ctrl key to start the game... <Ctrl_R>")
    wait_for_keyboard_trigger(keyboard.Key.ctrl_r)


def get_more_pressed_key(amount: int) -> keyboard.Key | keyboard.KeyCode:
    """Returns the key that was pressed `amount` times"""
    previous_key: keyboard.Key | keyboard.KeyCode | None = None
    count = 0

    def _more_press_trigger(key: keyboard.Key) -> bool:
        nonlocal previous_key
        nonlocal count
        if key != previous_key:
            previous_key = key
            count = 1
        else:
            count += 1

        if count == amount:
            return False

        return True

    with keyboard.Listener(on_release=_more_press_trigger) as listener:  # type: ignore
        listener.join()

    assert previous_key is not None
    return previous_key


def wait_for_keyboard_trigger(key_trigger: keyboard.Key) -> None:
    """Returns as soon as a certain key is pressed/released"""

    def _press_trigger(key: keyboard.Key) -> bool:
        if key == key_trigger:
            return False

        return True

    with keyboard.Listener(on_release=_press_trigger) as listener:  # type: ignore
        listener.join()


@contextmanager
def move_mouse_back():
    initial_cursor_position = pyautogui.position()
    try:
        yield
    finally:
        pyautogui.moveTo(*initial_cursor_position)
        pyautogui.click(*initial_cursor_position)


def are_there_colours_in_a_PIL_image(
    PIL_image: Image.Image, colours_to_locate: Sequence["ColorValue"]
) -> bool:
    """Check if PIL image contains any of the colours we are searching for"""
    # TODO: faster approach could be just to check every nth (5th) pixel
    #   for being the colour we want, and return as soon as we find it

    # Getting the list of all colours in that image
    occurrences_and_colours = PIL_image.getcolors(maxcolors=4096)

    # Trying to locate our wanted colour there
    for _occurrence, colour in occurrences_and_colours:
        if colour in colours_to_locate:
            return True

    return False


def save_new_boundaries_into_config(
    chessboard_left_top_pixel: "Pixel",
    chessboard_right_bottom_pixel: "Pixel",
    website: str,
    file_name: str = "config.py",
) -> None:
    """Replaces chessboard pixel values in the config file.

    WARNING: this is a hacky/fragile way of doing it.
    """
    with open(file_name, "r") as file:
        lines = file.readlines()

    we_are_in_good_place = False
    left_replaced = False
    right_replaced = False
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            continue

        if "self.website" in line and website in line:
            we_are_in_good_place = True
            continue
        if not we_are_in_good_place:
            continue

        # Replacing the values with new pixels
        if not left_replaced:
            if "self.chessboard_left_top_pixel" in line:
                second_half = line.split("=", maxsplit=1)[1]
                lines[i] = line.replace(second_half, f" {chessboard_left_top_pixel}\n")
                left_replaced = True
        if not right_replaced:
            if "self.chessboard_right_bottom_pixel" in line:
                second_half = line.split("=", maxsplit=1)[1]
                lines[i] = line.replace(
                    second_half, f" {chessboard_right_bottom_pixel}\n"
                )
                right_replaced = True

        if left_replaced and right_replaced:
            break

    with open(file_name, "w") as file:
        file.writelines(lines)
