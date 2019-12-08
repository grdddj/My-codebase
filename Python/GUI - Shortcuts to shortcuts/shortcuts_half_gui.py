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

from pynput.keyboard import Key, Listener, KeyCode
import pyautogui

class Methods:
    """
    Defining all the functions that are binded to key-events
    """

    def alt_tab():
        print("Alt + tab")
        pyautogui.hotkey('alt', 'tab')

    def ctrl_c():
        print("Ctrl + c")
        pyautogui.hotkey('ctrl', 'c')

    def ctrl_v():
        print("Ctrl + v")
        pyautogui.hotkey('ctrl', 'v')

    def ctrl_w():
        print("Ctrl + w")
        pyautogui.hotkey('ctrl', 'w')

class Config:
    """
    Defining the settings of which keys to listen for
        and which actions to bind to them
    """

    # Storing the last key pressed to identify double press of special keys
    last_key_pressed = ""

    # Defining special keys to stop listening and to change the mode
    key_to_stop = Key.esc
    key_to_change = Key.pause

    # Defining for which keys to listen in specified mode
    # Putting the keys into a list to enable more keys to be listened to
    keys_to_listen_in_certain_mode = {
        "Alt+Tab": [Key.ctrl_r],
        "Ctrl+C": [Key.ctrl_r],
        "Ctrl+V": [Key.ctrl_r],
        "Ctrl+W": [Key.ctrl_r]
    }

    # Defining which action to perform in specified mode
    actions_to_perform_in_certain_mode = {
        "Alt+Tab": Methods.alt_tab,
        "Ctrl+C": Methods.ctrl_c,
        "Ctrl+V": Methods.ctrl_v,
        "Ctrl+W": Methods.ctrl_w
    }

    # List of all available modes
    all_modes_list = list(keys_to_listen_in_certain_mode.keys())

    # Mode we are currently in
    current_mode = all_modes_list[0]

def choose_mode():
    """
    Shows a popup with the choice of all possible modes,
        so user can choose one
    """

    # Getting the new mode from user input, and in case it is not None
    #   (when user did not click any option), assign the new mode
    new_mode = pyautogui.confirm(text='Choose mode:',
                                 title='MODE',
                                 buttons=Config.all_modes_list)

    if new_mode:
        Config.current_mode = new_mode
        print("Mode switched to '{}'!".format(new_mode))

def on_release(key):
    """
    What to do when a key is released - listen to specified keys and
        performing actions according to it
    """

    # Stopping and changing keys must be pressed two times in a row to have effect
    if key == Config.key_to_stop and Config.last_key_pressed == Config.key_to_stop:
        listener.stop()
        pyautogui.alert(
            text="Thank you for using the service!",
            title='SEE YOU SOON',
            button='Goodbye!')

    if key == Config.key_to_change and Config.last_key_pressed == Config.key_to_change:
        choose_mode()
    Config.last_key_pressed = key

    # Identifying the current action keys depending on current mode
    if key in Config.keys_to_listen_in_certain_mode[Config.current_mode]:
        to_do = Config.actions_to_perform_in_certain_mode[Config.current_mode]
        to_do()

# Listening for keyboard events
if __name__ == "__main__":
    welcome_text = "Welcome to the keyboard shortcut script!\n" + \
        "You current mode is '{}'.\n".format(Config.current_mode) + \
        "Press (Pause/Break) key two times to open the choice of modes.\n" + \
        "Press (Esc) key two times to terminate the script.\n" + \
        "And what to do to trigger action? Try pressing right Control :)\n"

    print(welcome_text)
    with Listener(on_release=on_release) as listener:
        listener.join()
