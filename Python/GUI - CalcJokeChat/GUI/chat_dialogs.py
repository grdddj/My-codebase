import tkinter as tk
from tkinter import filedialog
from typing import List, Tuple

import chat_logger


class Dialogs:
    def __init__(self, parent, root_gui) -> None:
        self.parent = parent
        self.root_gui = root_gui

        self.log_identifier = "DIALOGS"

        self.success_color = "lime green"
        self.error_color = "red"
        self.info_color = "orange"

        self.text_size = 25

    def last_update_downloading_finish(self, path_where_file_was_saved: str) -> None:
        self.log_info("last_update_downloading_finish")
        title = "Download finished!"
        message = (
            "New file is located at the same directory as the current one. "
            f"Name: {path_where_file_was_saved}."
        )

        self.show_success_message(title, message)

    def last_update_downloading_start(self) -> None:
        self.log_info("last_update_downloading_start")
        title = "Download started on the background."
        message = (
            "Download started, please be patient. You will be notified, "
            "when it will finish."
        )

        self.show_success_message(title, message)

    def last_update_download_problem(self, err: str) -> None:
        self.log_info("last_update_download_problem")
        title = "Download of last update failed!"
        message = (
            "We are sorry, downloading the last update failed for some reason. "
            f"Try that again. Err: {err}"
        )

        self.show_error_message(title, message)

    def sending_message_problem(self, err: str) -> None:
        self.log_info("sending_message_problem")
        title = "Message sending failed!"
        message = (
            "We are sorry, sending the message failed for some reason. "
            f"Try that again. Err: {err}"
        )

        self.show_error_message(title, message)

    def sending_smile_problem(self, err: str) -> None:
        self.log_info("sending_smile_problem")
        title = "Smile sending failed!"
        message = (
            "We are sorry, sending the smile failed for some reason. "
            f"Try that again. Err: {err}"
        )

        self.show_error_message(title, message)

    def file_downloaded_successfully(self, file_path_to_save: str) -> None:
        self.log_info("file_downloaded_successfully")
        title = "File download finished."
        message = f"File downloaded as '{file_path_to_save}'."

        self.show_success_message(title, message)

    def file_download_problem(self, err: str) -> None:
        self.log_info("file_download_problem")
        title = "File download failed!"
        message = (
            "We are sorry, downloading the file failed for some reason. "
            f"Try that again. Err: {err}"
        )

        self.show_error_message(title, message)

    def file_uploaded_successfully(self, file_name: str) -> None:
        self.log_info("file_uploaded_successfully")
        title = "Upload finished."
        message = f"File upload of '{file_name}' finished!"

        self.show_success_message(title, message)

    def file_upload_problem(self, err: str) -> None:
        self.log_info("file_upload_problem")
        title = "File upload failed!"
        message = (
            "We are sorry, uploading the file failed for some reason. "
            f"Try that again. Err: {err}"
        )

        self.show_error_message(title, message)

    def picture_upload_problem(self, err: str) -> None:
        self.log_info("picture_upload_problem")
        title = "Picture upload failed!"
        message = (
            "We are sorry, uploading the picture failed for some reason. "
            f"Try that again. Err: {err}"
        )

        self.show_error_message(title, message)

    def name_change_successful(self) -> None:
        self.log_info("name_change_successful")
        title = "Name changed!"
        message = "Your name was changed. Have fun with your new identity!"

        self.show_success_message(title, message)

    def name_change_empty_name(self) -> None:
        self.log_info("name_change_empty_name")
        title = "No empty names!"
        message = "Empty names are not allowed. Who would then recognize you?"

        self.show_error_message(title, message)

    def name_change_cancelling(self) -> None:
        self.log_info("name_change_cancelling")
        title = "Out of ideas?"
        message = "Did not come up with a good name? Try looking at the calendar."

        self.show_error_message(title, message)

    def message_copied_into_clipboard(self, message: str) -> None:
        self.log_info("message_copied_into_clipboard")
        title = "Copied into clipboard"
        message = f"Message coppied into clipboard - {message}."

        self.show_success_message(title, message)

    def spell_check_is_successful(self) -> None:
        self.log_info("spell_check_was_successful")
        title = "Everything is fine!"
        message = "Congratulations. You spell like a boss!"

        self.show_success_message(title, message)

    def spell_check_uncovered_problems(
        self, corrected_words: List[Tuple[str, str]]
    ) -> None:
        self.log_info("spell_check_uncovered_problems")
        title = "There are some corrections"

        corrections = [
            f"{mistake} -> {suggested}" for mistake, suggested in corrected_words
        ]
        corrections_to_display = "\n".join(corrections)
        message = (
            f"Consider looking at the suggested corrections: \n{corrections_to_display}"
        )

        self.show_error_message(title, message)

    def should_the_latest_version_really_be_downloaded(self, last_update: str) -> bool:
        self.log_info("should_the_latest_version_really_be_downloaded")
        title = "Getting the latest version"
        question = (
            f"Last update released {last_update}. Do you really want to download it?"
        )

        dialog = YesOrNoDialog(
            parent=self.parent.support_window, title=title, question=question
        )
        self.place_the_window_to_the_center_of_the_screen(dialog.dialog_window)
        self.root_gui.wait_window(dialog.dialog_window)

        result = dialog.result
        return result == "yes"

    def should_the_file_really_be_downloaded(self, file_name: str) -> bool:
        self.log_info("should_the_file_really_be_downloaded")
        title = "Getting the file"
        question = f'Do you really want to download the file "{file_name}"?'

        dialog = YesOrNoDialog(
            parent=self.parent.support_window, title=title, question=question
        )
        self.place_the_window_to_the_center_of_the_screen(dialog.dialog_window)
        self.root_gui.wait_window(dialog.dialog_window)

        result = dialog.result
        return result == "yes"

    def get_new_name(self, user_name: str) -> str:
        self.log_info("get_new_name")
        dialog = NameChangeDialog(parent=self.parent.support_window, old_name=user_name)

        self.place_the_window_to_the_center_of_the_screen(dialog.dialog_window)
        self.root_gui.wait_window(dialog.dialog_window)

        name = dialog.username or "Unknown name"
        return name

    def get_file_path(self) -> str:
        self.log_info("get_file_path")
        file_path = filedialog.askopenfilename(parent=self.parent.support_window)
        return file_path

    def handle_empty_message(self) -> None:
        self.log_info("handle_empty_message")
        title = "No empty messages!"
        message = "Sending empty messages is not cool..."

        self.show_error_message(title, message)

    def block_support(self) -> None:
        self.log_info("block_support")
        message = "You thought it is so easy?"
        title = "Blocking support"

        self.show_error_message(title, message)

    def show_success_message(self, title: str, message: str) -> None:
        colour = self.success_color
        font_size = self.text_size

        self.show_message_on_top(
            message=message, colour=colour, font_size=font_size, title=title
        )

    def show_error_message(self, title: str, message: str) -> None:
        colour = self.error_color
        font_size = self.text_size

        self.show_message_on_top(
            message=message, colour=colour, font_size=font_size, title=title
        )

    def show_message_on_top(
        self, message: str, colour: str, font_size: int, title: str
    ) -> None:
        message_window = tk.Toplevel(self.parent.support_window, bg=colour)
        message_window.title(title)

        destroy_events = ["<Escape>", "<Return>", "<Button-1>"]
        for destroy_event in destroy_events:
            message_window.bind(destroy_event, lambda event: message_window.destroy())

        message_label = tk.Label(
            message_window,
            text=message,
            bg=colour,
            font=("Calibri", font_size),
            justify="center",
            bd=4,
            borderwidth=40,
        )
        message_label.pack()

        self.place_the_window_to_the_center_of_the_screen(message_window)

    def place_the_window_to_the_center_of_the_screen(self, window) -> None:
        self.root_gui.eval(f"tk::PlaceWindow {str(window)} center")

    def log_info(self, message) -> None:
        chat_logger.info(f"{self.log_identifier} - {message}")


class NameChangeDialog:
    def __init__(self, parent, old_name: str) -> None:
        self.dialog_window = tk.Toplevel(parent, bg="orange")
        self.dialog_window.title("Name change")

        font = ("Calibri", 20)

        text = f'Your current name is "{old_name}". What should be your new name?'
        self.label = tk.Label(self.dialog_window, text=text, font=font, bg="orange")
        self.label.pack()

        self.entry = tk.Entry(self.dialog_window, font=font)
        self.entry.pack()
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda event: self.send())

        self.submit_button = tk.Button(
            self.dialog_window,
            text="Submit",
            bg="lime green",
            font=font,
            command=self.send,
        )
        self.submit_button.pack()

        self.username = None

    def send(self) -> None:
        self.username = self.entry.get()
        self.dialog_window.destroy()


class YesOrNoDialog:
    def __init__(self, parent, title: str, question: str) -> None:
        self.dialog_window = tk.Toplevel(parent, bg="orange")
        self.dialog_window.title(title)

        font = ("Calibri", 20)

        top = tk.Frame(self.dialog_window, bg="orange")
        bottom = tk.Frame(self.dialog_window, bg="orange")
        top.pack(side=tk.TOP)
        bottom.pack(side=tk.BOTTOM)

        self.label = tk.Label(
            self.dialog_window, text=question, font=font, bg="orange", borderwidth=10
        )
        self.label.pack(in_=top, side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.yes_button = tk.Button(
            self.dialog_window,
            text="Yes",
            bg="lime green",
            font=font,
            command=self.send_yes,
            borderwidth=5,
        )
        self.yes_button.pack(in_=bottom, side=tk.LEFT)

        self.no_button = tk.Button(
            self.dialog_window,
            text="No",
            bg="red",
            font=font,
            command=self.send_no,
            borderwidth=5,
        )
        self.no_button.pack(in_=bottom, side=tk.LEFT)

        self.result = ""

    def send_yes(self) -> None:
        self.result = "yes"
        self.dialog_window.destroy()

    def send_no(self) -> None:
        self.result = "no"
        self.dialog_window.destroy()
