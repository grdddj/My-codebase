"""
This script is acting as a shortcut to keyboard shortcuts.
It is mapping individual keys to customized keyboard shortcuts,
    or in general to customized python functions.
"""

from pynput.keyboard import Key, Listener
import pyautogui


class ShortcutsToShortcuts:
    """
    Defining the settings of which keys to listen for
        and which actions to bind to them

    Defining all the functions that are binded to key-events
    """

    def __init__(self):
        # Whether to listen or not - way to control it from outside
        self.listen = True

        # Defining for which keys to listen in specified mode
        # Putting the keys into a list to enable more keys to be listened to
        self.keys_to_listen_in_certain_mode = {
            "Alt+Tab": [Key.ctrl_r],
            "Ctrl+C": [Key.ctrl_r],
            "Ctrl+V": [Key.ctrl_r],
            "Ctrl+W": [Key.ctrl_r],
            "Play+Pause": [Key.alt_r],
        }

        # Defining which action to perform in specified mode
        self.actions_to_perform_in_certain_mode = {
            "Alt+Tab": self.alt_tab,
            "Ctrl+C": self.ctrl_c,
            "Ctrl+V": self.ctrl_v,
            "Ctrl+W": self.ctrl_w,
            "Play+Pause": self.play_pause,
        }

        # List of all available modes
        self.all_modes_list = list(self.keys_to_listen_in_certain_mode.keys())

        # Mode we are currently in
        self.current_mode = self.all_modes_list[0]

    def set_new_mode(self, new_mode):
        self.current_mode = new_mode

    def alt_tab(self):
        pyautogui.hotkey('alt', 'tab')

    def ctrl_c(self):
        pyautogui.hotkey('ctrl', 'c')

    def ctrl_v(self):
        pyautogui.hotkey('ctrl', 'v')

    def ctrl_w(self):
        pyautogui.hotkey('ctrl', 'w')

    def play_pause(self):
        pyautogui.press("playpause")

    def on_release(self, key):
        """
        What to do when a key is released - listen to specified keys and
            performing actions according to it
        """
        if self.listen:
            # Identifying the current action keys depending on current mode
            if key in self.keys_to_listen_in_certain_mode[self.current_mode]:
                to_do = self.actions_to_perform_in_certain_mode[self.current_mode]
                to_do()

    def start_listening_loop(self):
        with Listener(on_release=self.on_release) as listener:
            listener.join()


# Listening for keyboard events
if __name__ == "__main__":
    shortcuts = ShortcutsToShortcuts()
    shortcuts.start_listening_loop()
