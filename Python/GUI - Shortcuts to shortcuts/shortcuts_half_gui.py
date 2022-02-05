"""
This script is acting as a shortcut to keyboard shortcuts.
It is mapping individual keys to customized keyboard shortcuts.
As an action key I prefer right Control, as it is almost not
    used anywhere else (and is not writing anything on the screen).
Pressing stop key (Esc) two times will terminate the listening, and
    pressing (Pause/Break) key two times is opening the choice of modes,
    where we can pick which actions to perform when action key is pressed
Probably the first time ever I used the (Pause/Break) key!
"""

from typing import Optional

import pyautogui
from pynput.keyboard import Key, Listener


class Methods:
    """
    Defining all the functions that are binded to key-events
    """

    @staticmethod
    def alt_tab() -> None:
        print("Alt + tab")
        pyautogui.hotkey("alt", "tab")

    @staticmethod
    def ctrl_c() -> None:
        print("Ctrl + c")
        pyautogui.hotkey("ctrl", "c")

    @staticmethod
    def ctrl_v() -> None:
        print("Ctrl + v")
        pyautogui.hotkey("ctrl", "v")

    @staticmethod
    def ctrl_w() -> None:
        print("Ctrl + w")
        pyautogui.hotkey("ctrl", "w")


class Config:
    """
    Defining the settings of which keys to listen for
        and which actions to bind to them
    """

    # Storing the last key pressed to identify double press of special keys
    last_key_pressed: Optional[Key] = None

    # Defining special keys to stop listening and to change the mode
    key_to_stop = Key.esc
    key_to_change = Key.pause

    action_key = Key.ctrl_r

    # Defining for which keys to listen in specified mode
    # Putting the keys into a list to enable more keys to be listened to
    keys_to_listen_in_certain_mode = {
        "Alt+Tab": [action_key],
        "Ctrl+C": [action_key],
        "Ctrl+V": [action_key],
        "Ctrl+W": [action_key],
    }

    # Defining which action to perform in specified mode
    actions_to_perform_in_certain_mode = {
        "Alt+Tab": Methods.alt_tab,
        "Ctrl+C": Methods.ctrl_c,
        "Ctrl+V": Methods.ctrl_v,
        "Ctrl+W": Methods.ctrl_w,
    }

    # List of all available modes
    all_modes_list = list(keys_to_listen_in_certain_mode.keys())

    # Mode we are currently in
    current_mode = all_modes_list[0]


def choose_mode() -> None:
    """
    Shows a popup with the choice of all possible modes,
        so user can choose one
    """

    # Getting the new mode from user input, and in case it is not None
    #   (when user did not click any option), assign the new mode
    new_mode = pyautogui.confirm(
        text="Choose mode:", title="MODE", buttons=Config.all_modes_list
    )

    if new_mode:
        Config.current_mode = new_mode
        print(f"Mode switched to '{new_mode}'!")


def on_release(key: Key) -> None:
    """
    What to do when a key is released - listen to specified keys and
        performing actions according to it
    """

    # Stopping and changing keys must be pressed two times in a row to have effect
    if key == Config.key_to_stop and Config.last_key_pressed == Config.key_to_stop:
        listener.stop()
        pyautogui.alert(
            text="Thank you for using the service!",
            title="SEE YOU SOON",
            button="Goodbye!",
        )

    if key == Config.key_to_change and Config.last_key_pressed == Config.key_to_change:
        choose_mode()

    Config.last_key_pressed = key

    # Identifying the current action keys depending on current mode
    if key in Config.keys_to_listen_in_certain_mode[Config.current_mode]:
        to_do = Config.actions_to_perform_in_certain_mode[Config.current_mode]
        to_do()


# Listening for keyboard events
if __name__ == "__main__":
    welcome_text = (
        "Welcome to the keyboard shortcut script!\n"
        f"You current mode is '{Config.current_mode}'.\n"
        f"Press ({Config.key_to_change}) key two times to open the choice of modes.\n"
        f"Press ({Config.key_to_stop}) key two times to terminate the script.\n"
        f"And what to do to trigger action? Try pressing ({Config.action_key}) :)\n"
    )

    print(welcome_text)
    with Listener(on_release=on_release) as listener:
        listener.join()
