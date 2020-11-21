import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

import chat_logger


class Dialogs:
    def __init__(self, parent, root_gui):
        self.parent = parent
        self.root_gui = root_gui

        self.log_identifier = "DIALOGS"

    def last_update_downloading_finish(self, path_where_file_was_saved):
        self.log_info("last_update_downloading_finish")
        title = "Download finished!"
        message = ("New file is located at the same directory as the current one. "
                   f"Name: {path_where_file_was_saved}.")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def last_update_downloading_start(self):
        self.log_info("last_update_downloading_start")
        title = "Download started on the background."
        message = ("Download started, please be patient. You will be notified, "
                   "when it will finish.")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def last_update_download_problem(self, err):
        self.log_info("last_update_download_problem")
        title = "Download of last update failed!"
        message = ("We are sorry, downloading the last update failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def sending_message_problem(self, err):
        self.log_info("sending_message_problem")
        title = "Message sending failed!"
        message = ("We are sorry, sending the message failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def sending_smile_problem(self, err):
        self.log_info("sending_smile_problem")
        title = "Smile sending failed!"
        message = ("We are sorry, sending the smile failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def file_downloaded_successfully(self, file_path_to_save):
        self.log_info("file_downloaded_successfully")
        title = "File download finished."
        message = f"File downloaded as '{file_path_to_save}'."
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def file_download_problem(self, err):
        self.log_info("file_download_problem")
        title = "File download failed!"
        message = ("We are sorry, downloading the file failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def file_uploaded_successfully(self, file_name):
        self.log_info("file_uploaded_successfully")
        title = "Upload finished."
        message = f"File upload of '{file_name}' finished!"
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def file_upload_problem(self, err):
        self.log_info("file_upload_problem")
        title = "File upload failed!"
        message = ("We are sorry, uploading the file failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def picture_upload_problem(self, err):
        self.log_info("picture_upload_problem")
        title = "Picture upload failed!"
        message = ("We are sorry, uploading the picture failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def name_change_successful(self):
        self.log_info("name_change_successful")
        title = "Name changed!"
        message = "Your name was changed. Have fun with your new identity!"
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def name_change_empty_name(self):
        self.log_info("name_change_empty_name")
        title = "No empty names!"
        message = "Empty names are not allowed. Who would then recognize you?"
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def name_change_cancelling(self):
        self.log_info("name_change_cancelling")
        title = "Out of ideas?"
        message = "Did not come up with a good name? Try looking at the calendar."
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def message_copied_into_clipboard(self, message):
        self.log_info("message_copied_into_clipboard")
        title = "Copied into clipboard"
        message = f"Message coppied into clipboard - {message}."
        messagebox.showinfo(title, message, parent=self.parent.support_window)

    def spell_check_is_successful(self):
        self.log_info("spell_check_was_successful")
        title = "Everything is fine!"
        message = "Congratulations. You spell like a boss!"
        colour = "lime green"
        font_size = 25
        geometry = "700x100"
        self.show_message_on_top(on_top_window=self.parent.support_window,
                                 message=message, colour=colour,
                                 font_size=font_size, title=title, geometry=geometry)

    def spell_check_uncovered_problems(self, corrected_words):
        self.log_info("spell_check_uncovered_problems")
        title = "There are some corrections"

        corrections = [f"{mistake} -> {suggested}" for mistake, suggested in corrected_words]
        corrections_to_display = "\n".join(corrections)
        message = f"Consider looking at the suggested corrections: \n{corrections_to_display}"

        colour = "tomato"
        font_size = 25
        geometry = "800x400"
        self.show_message_on_top(on_top_window=self.parent.support_window,
                                 message=message, colour=colour,
                                 font_size=font_size, title=title, geometry=geometry)

    def should_the_latest_version_really_be_downloaded(self, last_update):
        self.log_info("should_the_latest_version_really_be_downloaded")
        title = 'Get latest version'
        question = f'Last update released {last_update}. Do you really want to download it?'
        should_get_latest_version = messagebox.askquestion(
            title, question, icon='warning', parent=self.parent.support_window)

        return should_get_latest_version == "yes"

    def should_the_file_really_be_downloaded(self, file_name):
        self.log_info("should_the_file_really_be_downloaded")
        title = 'Get the file'
        question = f'Do you really want to download the file "{file_name}"?'
        should_download_the_file = messagebox.askquestion(
            title, question, icon='warning', parent=self.parent.support_window)

        return should_download_the_file == "yes"

    def get_new_name(self, user_name):
        self.log_info("get_new_name")
        question = f"Your current name is \"{user_name}\". What should be your new name?"
        new_name = simpledialog.askstring("New name", question, parent=self.parent.support_window)
        return new_name

    def get_file_path(self):
        self.log_info("get_file_path")
        file_path = filedialog.askopenfilename(parent=self.parent.support_window)
        return file_path

    def handle_empty_message(self):
        self.log_info("handle_empty_message")
        title = "No empty messages!"
        message = "Sending empty messages is not cool. You would not send empty envelopes either."
        colour = "red"
        font_size = 15
        geometry = "750x100"
        self.show_message_on_top(on_top_window=self.parent.support_window,
                                 message=message, colour=colour,
                                 font_size=font_size, title=title, geometry=geometry)

    def block_support(self):
        self.log_info("block_support")
        message = "You thought it is so easy?"
        title = "Blocking support"
        colour = "red"
        font_size = 25
        geometry = "400x100"
        self.show_message_on_top(on_top_window=self.parent.support_window,
                                 message=message, colour=colour,
                                 font_size=font_size, title=title, geometry=geometry)

    # TODO: show the message on the center of screen
    # TODO: maybe calculate the dimensions according to the text
    def show_message_on_top(self, on_top_window, message, colour, font_size, title, geometry):
        message_window = tk.Toplevel(on_top_window)
        message_window.title(title)
        message_window.geometry(geometry)

        message_label = tk.Label(message_window, text=message, bg=colour,
                                 font=("Calibri", font_size), justify="center", bd=4)
        message_label.place(relheight=1, relwidth=1)

        self.place_the_window_to_the_center_of_the_screen(message_window)

    def place_the_window_to_the_center_of_the_screen(self, window):
        self.root_gui.eval(f'tk::PlaceWindow {str(window)} center')

    def log_info(self, message):
        chat_logger.info(f"{self.log_identifier} - {message}")
