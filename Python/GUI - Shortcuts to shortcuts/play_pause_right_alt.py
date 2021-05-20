from pynput.keyboard import Key, Listener
import pyautogui


class ShortcutsToShortcuts:
    def __init__(self):
        self.listen = True
        self.keys_to_listen_in_certain_mode = {
            "Play+Pause": [Key.alt_r],
        }

        self.actions_to_perform_in_certain_mode = {
            "Play+Pause": self.play_pause,
        }

        self.all_modes_list = list(self.keys_to_listen_in_certain_mode.keys())
        self.current_mode = self.all_modes_list[0]

    def play_pause(self):
        pyautogui.press("playpause")

    def on_release(self, key):
        if self.listen:
            if key in self.keys_to_listen_in_certain_mode[self.current_mode]:
                to_do = self.actions_to_perform_in_certain_mode[self.current_mode]
                to_do()

    def start_listening_loop(self):
        with Listener(on_release=self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    shortcuts = ShortcutsToShortcuts()
    shortcuts.start_listening_loop()
