import time
import queue
import json
from PIL import ImageTk, Image
import websocket

import tkinter as tk
from tkinter import ttk

from config import Config
from chat_dialogs import Dialogs
import chat_threading_actions as actions
import chat_getting_messages as messages
import helpers
import chat_logger


class ScrollableFrameForMessages(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)

        # TODO: could request older messages automatically when the scrollbar
        #   would be at the top
        scrollbar = tk.Scrollbar(self, orient="vertical", cursor="hand2", command=self.canvas.yview)
        scrollbar.config(width=50)
        scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # There is a limit of labels that can accomodate to a tkinter Canvas (around 315)
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", self.adjust_scrolling_region)
        self.canvas.bind('<Configure>', self.adjust_frame_width)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        amount_of_units = int(-1*(event.delta/120))
        self.canvas.yview_scroll(amount_of_units, "units")

    def adjust_frame_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def adjust_scrolling_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class SupportWindow:
    def __init__(self, parent):
        self.parent = parent
        self.root_gui = parent.parent

        self.log_identifier = "GUI"

        self.dialogs = Dialogs(
            parent=self,
            root_gui=self.root_gui
        )

        # TODO: consider moving this to a separate thread, to have zero latency
        # TODO: improve the spellchecking logic - if the result is negative,
        #   check for every change probably, to give feedback that all is OK
        self.spell_checker = helpers.SpellChecker()
        self.spell_check_icon_ok = None
        self.schedule_spell_check_id = ""
        self.miliseconds_to_wait_before_spell_check = 500

        self.ip_address = helpers.get_ip_address()

        self.user_name = Config.NAME

        self.button_font = ("Calibri", 20, "bold")
        self.button_border = 5
        self.button_rel_x = 0.77
        self.button_rel_width = 0.2
        self.button_rel_height = 0.1

        self.log_info("Initializing websocket connection")
        # TODO: create some error handling, when the connection goes down
        # Probably an after() loop here, to check the connection and if down,
        #   recreate it and recreate the message sending object
        self.ws = websocket.create_connection(Config.MESSAGES_WEBSOCKET_URL)

    def on_destroy(self):
        self.log_info("Destroying the support window")

        # The message getting thread in the background must be killed
        self.getting_message_data_thread.stop()

        # To be sure the stop event is processed, before closing the WS
        time.sleep(0.1)

        self.log_info("Closing websocket connection")
        self.ws.close()

        self.support_window.destroy()

        if Config.DEBUG_MODE:
            self.root_gui.destroy()

        self.log_info("Support window successfully destroyed")

    def show_support_window(self):
        self.log_info("Showing the support window")
        self.support_window = tk.Toplevel(self.parent)
        self.support_window.title("Support")
        self.support_window.state("zoomed")

        # Destroying the component is connected with cleaning logic
        self.support_window.protocol("WM_DELETE_WINDOW", self.on_destroy)

        messaging_area = tk.Frame(self.support_window, bg="yellow", bd=10)
        messaging_area.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.messages_frame = ScrollableFrameForMessages(messaging_area)
        self.messages_frame.place(relx=0, rely=0, relheight=0.82, relwidth=0.70)

        self.is_other_writing_entry = tk.Entry(
            self.support_window, bg="light sea green",
            disabledbackground="light sea green",
            disabledforeground="black",
            font=("Calibri", 15), bd=5, state="disabled"
        )
        self.is_other_writing_entry.place(relx=0, rely=0.83, relheight=0.05, relwidth=0.7)

        self.should_send_entry_updates = tk.BooleanVar()
        self.should_send_entry_updates.set(True)
        self.entry_updates_checkbox = tk.Checkbutton(
            self.support_window, text="Send real-time entry updates",
            font=("Calibri", 15), bd=2,
            variable=self.should_send_entry_updates
        )
        self.entry_updates_checkbox.place(relx=0.77, rely=0.81, relheight=0.05)

        self.health_check_label = tk.Label(self.support_window)
        self.health_check_label.place(relx=0.97, rely=0.01, relheight=0.04, relwidth=0.03)
        self.set_health_check(ok=True)

        self.message_in_entry = tk.StringVar()
        self.message_in_entry.trace("w", self.handle_change_in_message_entry_text)

        self.message_entry = tk.Entry(
            self.support_window, textvariable=self.message_in_entry,
            bg="orange", font=("Calibri", 25), bd=5)
        self.message_entry.place(relx=0, rely=0.88, relheight=0.08, relwidth=0.7)
        self.message_entry.focus_set()
        self.message_entry.bind("<Return>", (lambda event: self.process_message_from_entry()))

        self.spell_check_label = tk.Label(
            self.support_window, width=64, height=64, cursor="hand2")
        self.spell_check_label.place(relx=0.7, rely=0.87)
        self.spell_check_label.bind('<Button-1>', lambda event: self.handle_spellcheck_window())
        self.set_spell_check_icon(ok=True)

        self.answer_to_message_entry = tk.Entry(
            self.support_window, bg="yellow", font=("Calibri", 13),
            disabledbackground="yellow", disabledforeground="black",
            bd=0, state="disabled"
        )
        self.answer_to_message_entry.place(relx=0, rely=0.96, relheight=0.04, relwidth=0.7)

        block_support_button = tk.Button(
            self.support_window, text="Block support",
            bg="tomato", bd=self.button_border, cursor="hand2",
            font=self.button_font, command=self.dialogs.block_support
        )
        block_support_button.place(
            relx=self.button_rel_x,
            rely=0.01,
            relheight=self.button_rel_height,
            relwidth=self.button_rel_width
        )

        download_latest_version_button = tk.Button(
            self.support_window, text="Get latest version",
            bg="lime green", font=self.button_font,
            bd=self.button_border, cursor="hand2",
            command=self.get_latest_update
        )
        download_latest_version_button.place(
            relx=self.button_rel_x,
            rely=0.13,
            relheight=self.button_rel_height,
            relwidth=self.button_rel_width
        )

        change_name_button = tk.Button(
            self.support_window, text="Change name",
            bg="orange", font=self.button_font,
            bd=self.button_border, cursor="hand2",
            command=self.change_name
        )
        change_name_button.place(
            relx=self.button_rel_x,
            rely=0.25,
            relheight=self.button_rel_height,
            relwidth=self.button_rel_width
        )

        send_picture_button = tk.Button(
            self.support_window, text="Send picture",
            bg="MediumPurple1", font=self.button_font,
            bd=self.button_border, cursor="hand2",
            command=self.handle_picture_sending_dialog
        )
        send_picture_button.place(
            relx=self.button_rel_x,
            rely=0.37,
            relheight=self.button_rel_height,
            relwidth=self.button_rel_width
        )

        send_file_button = tk.Button(
            self.support_window, text="Send file",
            bg="SteelBlue1", font=self.button_font,
            bd=self.button_border, cursor="hand2",
            command=self.handle_file_sending_dialog
        )
        send_file_button.place(
            relx=self.button_rel_x,
            rely=0.49,
            relheight=self.button_rel_height,
            relwidth=self.button_rel_width
        )

        message_sending_button = tk.Button(
            self.support_window, text="Send message",
            bg="grey", font=self.button_font,
            bd=self.button_border, cursor="hand2",
            command=self.process_message_from_entry
        )
        message_sending_button.place(
            relx=self.button_rel_x,
            rely=0.88,
            relheight=self.button_rel_height,
            relwidth=self.button_rel_width
        )

        self.render_smiley_icons_to_be_clicked()

        # what_is_new_button - fetch from web on init and send response back that IP saw it

        self.start_getting_messages_in_the_background()

    def render_smiley_icons_to_be_clicked(self):
        self.log_info("Rendering smiley-icons")
        smileys_first_row = [
            "happy",
            "smiling",
            "wink",
            "unhappy",
        ]

        smileys_second_row = [
            "laughing",
            "thinking",
            "facepalm",
            "thumb-up",
        ]

        positions = [0.77, 0.83, 0.89, 0.95]

        def render_smiley(relx, rely, smile_type):
            file_name = f"smileys_icons/{smile_type}.png"
            file_path = helpers.get_resource_path(file_name)

            photo = ImageTk.PhotoImage(Image.open(file_path))

            smiley_face = tk.Label(
                self.support_window, image=photo, width=64, height=64, cursor="hand2")
            smiley_face.photo = photo
            smiley_face.place(relx=relx, rely=rely)
            smiley_face.bind('<Button-1>', lambda event: self.handle_smile_icon_click(smile_type))

        for index, smiley in enumerate(smileys_first_row):
            relx = positions[index]
            rely = 0.61
            smile_type = smiley
            render_smiley(relx, rely, smile_type)

        for index, smiley in enumerate(smileys_second_row):
            relx = positions[index]
            rely = 0.71
            smile_type = smiley
            render_smiley(relx, rely, smile_type)

    def handle_smile_icon_click(self, smile_type):
        self.log_info(f"Smile clicked - {smile_type}")
        self.message_sending_queue = queue.Queue()
        actions.SmileSending(
            queue=self.message_sending_queue,
            ws=self.ws,
            user_name=self.user_name,
            ip_address=self.ip_address,
            smile_type=smile_type
        ).start()
        self.parent.after(100, self.process_queue_for_smile_sending)

    def process_queue_for_smile_sending(self):
        try:
            msg = self.message_sending_queue.get(0)
            success = msg["success"]
            if not success:
                reason = msg["reason"]
                self.dialogs.sending_smile_problem(reason)
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_smile_sending)

    def handle_picture_sending_dialog(self):
        picture_path = self.dialogs.get_file_path()
        if not picture_path:
            return

        self.handle_picture_upload(picture_path)

    def handle_picture_upload(self, picture_path):
        self.picture_upload_queue = queue.Queue()
        actions.PictureUpload(
            queue=self.picture_upload_queue,
            ws=self.ws,
            picture_path=picture_path,
            user_name=self.user_name,
            ip_address=self.ip_address,
        ).start()
        self.parent.after(100, self.process_queue_for_picture_upload)

    def process_queue_for_picture_upload(self):
        try:
            msg = self.picture_upload_queue.get(0)
            success = msg["success"]
            if success:
                picture_name_saved = msg["file_name_saved"]
                self.dialogs.file_uploaded_successfully(picture_name_saved)
            else:
                reason = msg["reason"]
                self.dialogs.picture_upload_problem(reason)
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_picture_upload)

    def handle_file_sending_dialog(self):
        file_path = self.dialogs.get_file_path()
        if not file_path:
            return

        self.handle_file_upload(file_path)

    def handle_file_upload(self, file_path):
        self.file_upload_queue = queue.Queue()
        actions.FileUpload(
            queue=self.file_upload_queue,
            ws=self.ws,
            file_path=file_path,
            user_name=self.user_name,
            ip_address=self.ip_address,
        ).start()
        self.parent.after(100, self.process_queue_for_file_upload)

    def process_queue_for_file_upload(self):
        try:
            msg = self.file_upload_queue.get(0)
            success = msg["success"]
            if success:
                file_name_saved = msg["file_name_saved"]
                self.dialogs.file_uploaded_successfully(file_name_saved)
            else:
                reason = msg["reason"]
                self.dialogs.file_upload_problem(reason)
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_file_upload)

    def start_getting_messages_in_the_background(self):
        self.log_info("Starting to get messages on the background")
        self.getting_message_data_thread = messages.GettingMessageData(
            parent=self
        )
        self.getting_message_data_thread.start()

    def handle_file_download(self, file_name):
        if not self.dialogs.should_the_file_really_be_downloaded(file_name):
            return

        self.download_file(file_name)

    def download_file(self, file_name):
        self.file_download_queue = queue.Queue()
        actions.FileDownload(
            queue=self.file_download_queue,
            file_name=file_name
        ).start()
        self.parent.after(100, self.process_queue_for_file_download)

    def process_queue_for_file_download(self):
        try:
            msg = self.file_download_queue.get(0)
            success = msg["success"]
            if success:
                file_path_to_save = msg["file_path_to_save"]
                self.dialogs.file_downloaded_successfully(file_path_to_save)
            else:
                reason = msg["reason"]
                self.dialogs.file_download_problem(reason)
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_file_download)

    def spell_check_the_message(self, message):
        result = self.spell_checker.check_the_text_for_errors(message)
        if result['success']:
            self.log_info(f"Finished spellcheck - SUCCESS - '{message}'")
        else:
            corrections = result["corrected_words"]
            self.log_info(f"Finished spellcheck - FAILURE - '{message}' - '{corrections}'")

        self.set_spell_check_icon(ok=result["success"])

    def set_spell_check_icon(self, ok=True):
        if self.spell_check_icon_ok == ok:
            return
        else:
            self.spell_check_icon_ok == ok

        if ok:
            file_name = "icons/grammarly_icon_green.png"
        else:
            file_name = "icons/grammarly_icon_red.png"

        file_path = helpers.get_resource_path(file_name)

        photo = ImageTk.PhotoImage(Image.open(file_path))
        self.spell_check_label.configure(image=photo)
        self.spell_check_label.photo = photo

    def handle_spellcheck_window(self):
        message = self.get_text_from_message_entry()
        result = self.spell_checker.check_the_text_for_errors(message)
        if result["success"]:
            self.dialogs.spell_check_is_successful()
        else:
            self.dialogs.spell_check_uncovered_problems(result["corrected_words"])

    def schedule_spell_check(self, message):
        try:
            self.root_gui.after_cancel(self.schedule_spell_check_id)
        except ValueError:
            pass
        self.schedule_spell_check_id = self.root_gui.after(
            self.miliseconds_to_wait_before_spell_check,
            lambda: self.spell_check_the_message(message)
        )

    def handle_change_in_message_entry_text(self, *args):
        message = self.get_text_from_message_entry()
        self.schedule_spell_check(message)
        self.send_message_entry_to_websocket(message)

    def send_message_entry_to_websocket(self, message):
        if not self.should_send_entry_updates.get():
            if message:
                message = "Writing..."

        to_send = {
            "message_type": "entry_update",
            "ip_address": self.ip_address,
            "message": message,
            "update": True,
        }

        json_to_send = json.dumps(to_send)
        self.ws.send(json_to_send)

    def process_message_from_entry(self):
        message = self.get_text_from_message_entry()
        self.log_info(f"Processing message from entry - {message}")

        if not message:
            return self.dialogs.handle_empty_message()
        else:
            return self.handle_message_sending(message)

    def handle_message_sending(self, message):
        self.clean_message_entry()
        self.focus_on_message_entry()

        self.message_sending_queue = queue.Queue()
        actions.MessageSending(
            queue=self.message_sending_queue,
            ws=self.ws,
            user_name=self.user_name,
            ip_address=self.ip_address,
            message=message,
            answer_to_message=self.get_answer_to_message()
        ).start()
        self.parent.after(100, self.process_queue_for_message_sending)

        self.empty_answer_to_message_entry()
        self.show_answer_to_message_cancel_label(show=False)
        self.set_spell_check_icon(ok=True)

    def get_answer_to_message(self):
        entry_content = self.answer_to_message_entry.get()
        string_at_beginning = "Answer to: "
        if entry_content.startswith(string_at_beginning):
            length_to_cut = len(string_at_beginning)
            return entry_content[length_to_cut:]
        else:
            return entry_content

    def handle_click_on_answer_to_cancelling_label(self):
        self.empty_answer_to_message_entry()
        self.show_answer_to_message_cancel_label(show=False)

    def empty_answer_to_message_entry(self):
        helpers.define_entry_content(self.answer_to_message_entry, "")

    def show_answer_to_message_cancel_label(self, show):
        label_name = "answer_to_message_cancel_label"
        if show:
            already_is_shown = hasattr(self, label_name)
            if already_is_shown:
                return

            label = tk.Label(
                self.support_window, bg="red", font=("Calibri", 15),
                bd=0, text="X", cursor="hand2"
            )
            label.bind('<Button-1>',
                lambda event: self.handle_click_on_answer_to_cancelling_label())
            label.place(relx=0.7, rely=0.96, relheight=0.04, relwidth=0.03)
            setattr(self, label_name, label)
        else:
            if hasattr(self, label_name):
                getattr(self, label_name).destroy()
                delattr(self, label_name)

    def process_queue_for_message_sending(self):
        try:
            msg = self.message_sending_queue.get(0)
            success = msg["success"]
            if not success:
                # TODO: could input the message back into the message entry
                reason = msg["reason"]
                self.dialogs.sending_message_problem(reason)
            self.focus_on_message_entry()
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_message_sending)

    def get_latest_update(self):
        last_update = helpers.get_the_time_of_last_update()
        if not self.dialogs.should_the_latest_version_really_be_downloaded(last_update):
            return

        self.handle_latest_update_download()

    def handle_latest_update_download(self):
        self.dialogs.last_update_downloading_start()

        self.latest_update_download_queue = queue.Queue()
        actions.LatestUpdateDownload(
            queue=self.latest_update_download_queue
        ).start()
        self.parent.after(100, self.process_queue_for_latest_update_download)

    def process_queue_for_latest_update_download(self):
        try:
            msg = self.latest_update_download_queue.get(0)
            success = msg["success"]
            if success:
                path_where_to_save_it = msg["path_where_to_save_it"]
                self.dialogs.last_update_downloading_finish(path_where_to_save_it)
            else:
                reason = msg["reason"]
                self.dialogs.last_update_download_problem(reason)
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_latest_update_download)

    def change_name(self):
        new_name = self.dialogs.get_new_name(self.user_name)
        self.log_info(f"New name chosen - {new_name}")

        if new_name:
            self.user_name = new_name
            self.dialogs.name_change_successful()
        else:
            if new_name == "":
                self.dialogs.name_change_empty_name()
            elif new_name is None:
                self.dialogs.name_change_cancelling()

    def set_health_check(self, ok):
        if ok:
            bg = "lime green"
            text = " OK  "
        else:
            bg = "tomato"
            text = "ERROR"

        self.health_check_label.configure(bg=bg, text=text)

    def get_text_from_message_entry(self):
        return self.message_in_entry.get()

    def clean_message_entry(self):
        self.log_info("Cleaning message entry")
        self.message_in_entry.set("")

    def focus_on_message_entry(self):
        self.message_entry.focus()

    def log_info(self, message):
        chat_logger.info(f"{self.log_identifier} - {message}")

    def log_exception(self, message):
        chat_logger.exception(f"{self.log_identifier} - {message}")
