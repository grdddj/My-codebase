"""
GUI for controlling of the shortcuts script.
It will adapt itself to all the new key-function bindings defined in
    shortcuts_full_gui_helper, so there should be no need to ever touch
    this GUI code again, apart from further features or design improvements.
"""

import sys
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QLabel,
    QMainWindow,
    QPushButton,
)
from shortcuts_full_gui_helper import ShortcutsToShortcuts


class ShortcutsGUI(QMainWindow):
    def __init__(self, shortcuts: ShortcutsToShortcuts) -> None:
        super().__init__()
        self.shortcuts = shortcuts
        self.left = 10
        self.top = 10
        self.title = "Shortcuts to shortcuts"
        self.width = 450
        self.height = 500
        self.welcome_text = (
            "Welcome to the keyboard shortcut script!\n"
            "Click whatever shortcut you would like to access quickly.\n"
            "Click STOP to stop listening, and START to listen again.\n"
            "What to do to trigger action? Try pressing right Control :)\n"
        )

        # Initialize the whole screen
        self.initUI()

        # Initialize our multithreading workers
        self.threadpool = QThreadPool()

    def initUI(self) -> None:
        """
        Completely initialize all the screen components
        """

        self.setWindowTitle(self.title)
        # Width was set to fit in the label text, heigth was guessed and will be
        #   determined precisely depending on the amount of buttons
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Positioning and filling the label with the welcome text for the user
        text_label_height = 100
        self.info_label = QLabel(self)
        self.info_label.move(0, 0)
        self.info_label.resize(self.width, text_label_height)
        self.info_label.setText(self.welcome_text)
        self.info_label.setFont(QFont("Times", 10, QFont.Bold))
        self.info_label.setStyleSheet("padding: 5px 5px 5px 5px;")

        # Defining how big the font in buttons should be and how they should
        #   be colored in their active and inactive states
        self.button_font_size = "font-size: 20px;"
        self.active_action_button_background = "background-color: green;"
        self.active_stop_button_background = "background-color: red;"
        self.inactive_button_background = "background-color: white;"

        # Including stop and start buttons
        start_stop_button_width = 100
        start_stop_button_height = 100
        distance_between_start_stop_buttons = 10
        self.stop_button = QPushButton("STOP", self)
        self.stop_button.move(self.width - start_stop_button_width, text_label_height)
        self.stop_button.resize(start_stop_button_width, start_stop_button_height)
        self.stop_button.setStyleSheet(
            "{}{}".format(self.inactive_button_background, self.button_font_size)
        )
        self.stop_button.pressed.connect(lambda: self.stop_listening())

        self.start_button = QPushButton("START", self)
        self.start_button.move(
            self.width - start_stop_button_width,
            2 * text_label_height + distance_between_start_stop_buttons,
        )
        self.start_button.resize(start_stop_button_width, start_stop_button_height)
        self.start_button.setStyleSheet(
            "{}{}".format(self.inactive_button_background, self.button_font_size)
        )
        self.start_button.pressed.connect(lambda: self.start_listening())

        # Rendering all the shortcut action buttons
        action_button_width = 150
        action_button_height = 50
        distance_between_action_buttons = 10
        for index, mode in enumerate(self.shortcuts.all_modes_list):
            setattr(self, mode, QPushButton(mode, self))
            getattr(self, mode).move(
                0,
                text_label_height
                + index * (action_button_height + distance_between_action_buttons),
            )
            getattr(self, mode).resize(action_button_width, action_button_height)
            getattr(self, mode).setStyleSheet(self.button_font_size)
            getattr(self, mode).pressed.connect(
                lambda mode=mode: self.set_new_mode_and_reflect_it(mode)
            )

        # Put red background to the active mode, and white to all others
        self.highlight_specific_button(self.shortcuts.current_mode)

        # Calculating the overall height to cut the window nicely
        overall_height = text_label_height + max(
            len(self.shortcuts.all_modes_list)
            * (action_button_height + distance_between_action_buttons),
            2 * (start_stop_button_height + distance_between_start_stop_buttons),
        )

        # Fixing the size, not to allow any resize, which would look bad
        # self.setFixedSize(self.size())
        self.setFixedSize(self.width, overall_height)

        # Helpers to place the window to the center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # Showing the whole component
        self.show()

    def set_new_mode_and_reflect_it(self, new_mode: str) -> None:
        """
        Changing the mode according to user input
        Will send the change only if the "STOP" button is not active
        """

        if self.shortcuts.listen:
            self.shortcuts.set_new_mode(new_mode)
            self.highlight_specific_button(new_mode)

    def highlight_specific_button(self, button_name: str) -> None:
        """
        Makes clear that the current mode is easily recognizable in GUI
            by colouring the button that was just clicked
        """

        # Looping through all buttons apart from the "start_button", which
        #   does not need to be highlighted, and putting all the
        #   buttons to their inactive state, and only highlights the chosen one
        for mode in self.shortcuts.all_modes_list + ["stop_button"]:
            if mode == button_name:
                if mode != "stop_button":
                    getattr(self, mode).setStyleSheet(
                        f"{self.active_action_button_background}{self.button_font_size}"
                    )
                else:
                    getattr(self, mode).setStyleSheet(
                        f"{self.active_stop_button_background}{self.button_font_size}"
                    )
            else:
                getattr(self, mode).setStyleSheet(
                    f"{self.inactive_button_background}{self.button_font_size}"
                )

    def stop_listening(self) -> None:
        """
        Sends signal to stop listening for the keys and highlights
            the "STOP" button to make it apparent to the user
        """

        self.shortcuts.listen = False
        self.highlight_specific_button("stop_button")

    def start_listening(self) -> None:
        """
        Sends signal to start listening again and highlights
            the mode that is currently active
        """

        self.shortcuts.listen = True
        self.highlight_specific_button(self.shortcuts.current_mode)

    def run_listener(self) -> None:
        # Pass the function to execute
        worker = Worker(self.shortcuts.start_listening_loop)

        # Execute
        self.threadpool.start(worker)


class Worker(QRunnable):
    """
    Our multithreaded workers that will be working for us
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        result = self.fn(*self.args, **self.kwargs)


if __name__ == "__main__":
    # Necessary stuff for errors and exceptions to be thrown
    # Without this, the app just dies and says nothing
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook

    # Creating the window
    app = QApplication(sys.argv)
    ex = ShortcutsGUI(shortcuts=ShortcutsToShortcuts())

    # Running the listener in the background
    ex.run_listener()

    sys.exit(app.exec_())
