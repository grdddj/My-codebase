import os
import requests
import traceback
import queue
from datetime import datetime
from PIL import ImageTk, Image

import tkinter as tk
from tkinter import ttk

from config import Config
from chat_dialogs import Dialogs
import chat_threading_actions as actions
import helpers


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

        self.dialogs = Dialogs(self)

        self.confirmation_sent = False

        self.ip_address = helpers.get_ip_address()

        self.user_name = Config.NAME

        # Needed for the destroyment of infinite checking og messages
        self.after_loop_id = 0

        self.message_text_font = ("Helvetica", 16)
        self.message_background = "orange"
        self.message_anchor = tk.W

        self.button_font = ("Calibri", 20, "bold")
        self.button_border = 5
        self.button_rel_x = 0.75
        self.button_rel_width = 0.2
        self.button_rel_height = 0.1

    def on_destroy(self):
        print("Cancel, reset and destroy")
        # Making sure the after() function is not called anymore on the background
        self.parent.after_cancel(self.after_loop_id)

        # The message getting thread in the background must be killed
        self.getting_message_data_thread.stop()

        self.support_window.destroy()

    def show_support_window(self):
        self.support_window = tk.Toplevel(self.parent)
        self.support_window.title("Support")
        self.support_window.state("zoomed")

        # Destroying the component is connected with cleaning logic
        self.support_window.protocol("WM_DELETE_WINDOW", self.on_destroy)

        messaging_area = tk.Frame(self.support_window, bg="yellow", bd=10)
        messaging_area.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.messages_frame = ScrollableFrameForMessages(messaging_area)
        self.messages_frame.place(relx=0, rely=0, relheight=0.87, relwidth=0.70)

        self.message_entry = tk.Entry(self.support_window, bg="orange", font=("Calibri", 25), bd=5)
        self.message_entry.place(relx=0, rely=0.88, relheight=0.1, relwidth=0.7)
        self.message_entry.bind("<Return>", (lambda event: self.process_message_from_entry()))

        block_support_button = tk.Button(self.support_window, text="Block support",
                                         bg="tomato", bd=self.button_border, cursor="hand2",
                                         font=self.button_font, command=self.block_support)
        block_support_button.place(relx=self.button_rel_x,
                                   rely=0.01,
                                   relheight=self.button_rel_height,
                                   relwidth=self.button_rel_width)

        download_latest_version_button = tk.Button(self.support_window, text="Get latest version",
                                                   bg="lime green", font=self.button_font,
                                                   bd=self.button_border, cursor="hand2",
                                                   command=self.get_latest_update)
        download_latest_version_button.place(relx=self.button_rel_x,
                                             rely=0.13,
                                             relheight=self.button_rel_height,
                                             relwidth=self.button_rel_width)

        change_name_button = tk.Button(self.support_window, text="Change name",
                                       bg="orange", font=self.button_font,
                                       bd=self.button_border, cursor="hand2",
                                       command=self.change_name)
        change_name_button.place(relx=self.button_rel_x,
                                 rely=0.25,
                                 relheight=self.button_rel_height,
                                 relwidth=self.button_rel_width)

        send_picture_button = tk.Button(self.support_window, text="Send picture",
                                        bg="MediumPurple1", font=self.button_font,
                                        bd=self.button_border, cursor="hand2",
                                        command=self.handle_picture_sending_dialog)
        send_picture_button.place(relx=self.button_rel_x,
                                  rely=0.37,
                                  relheight=self.button_rel_height,
                                  relwidth=self.button_rel_width)

        send_file_button = tk.Button(self.support_window, text="Send file",
                                     bg="SteelBlue1", font=self.button_font,
                                     bd=self.button_border, cursor="hand2",
                                     command=self.handle_file_sending_dialog)
        send_file_button.place(relx=self.button_rel_x,
                               rely=0.49,
                               relheight=self.button_rel_height,
                               relwidth=self.button_rel_width)

        message_sending_button = tk.Button(self.support_window, text="Send message",
                                           bg="grey", font=self.button_font,
                                           bd=self.button_border, cursor="hand2",
                                           command=self.process_message_from_entry)
        message_sending_button.place(relx=self.button_rel_x,
                                     rely=0.88,
                                     relheight=self.button_rel_height,
                                     relwidth=self.button_rel_width)

        self.render_smiley_icons_to_be_clicked()

        # what_is_new_button - fetch from web on init and send response back that IP saw it

        self.start_getting_messages_in_the_background()

    def render_smiley_icons_to_be_clicked(self):
        smileys_first_row = [
            "happy",
            "smiling",
            "unhappy",
        ]

        smileys_second_row = [
            "laughing",
            "thinking",
            "thumb-up",
        ]

        positions = [0.75, 0.825, 0.90]

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
            rely = 0.63
            smile_type = smiley
            render_smiley(relx, rely, smile_type)

        for index, smiley in enumerate(smileys_second_row):
            relx = positions[index]
            rely = 0.75
            smile_type = smiley
            render_smiley(relx, rely, smile_type)

    def handle_smile_icon_click(self, smile_type):
        self.message_sending_queue = queue.Queue()
        actions.SmileSending(
            queue=self.message_sending_queue,
            user_name=self.user_name,
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
            picture_path=picture_path,
            user_name=self.user_name
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
            file_path=file_path,
            user_name=self.user_name
        ).start()
        self.parent.after(100, self.process_queue_for_file_upload)

    def process_queue_for_file_upload(self):
        try:
            msg = self.file_upload_queue.get(0)
            success = msg["success"]
            if success:
                file_name_saved = msg["file_name_saved"]
                self.file_uploaded_successfully(file_name_saved)
            else:
                reason = msg["reason"]
                self.dialogs.file_upload_problem(reason)
        except queue.Empty:
            self.parent.after(100, self.process_queue_for_file_upload)

    def start_getting_messages_in_the_background(self):
        self.message_queue = queue.Queue()
        self.getting_message_data_thread = actions.GettingMessageData(
            queue=self.message_queue
        )
        self.getting_message_data_thread.start()
        self.parent.after(100, self.update_messaging_area)

    def update_messaging_area(self):
        try:
            new_messages = self.message_queue.get(0)
            for message in new_messages:
                self.update_chat_messages(message)
        except queue.Empty:
            pass
            # print("queue is empty")
        except Exception as err:
            self.handle_problems_when_filling_message_area(err)

        self.call_the_message_updating_function_infinitely()

    def call_the_message_updating_function_infinitely(self):
        self.after_loop_id = self.parent.after(
            Config.chat_refresh_time_in_ms, self.update_messaging_area)

    def update_chat_messages(self, new_message):
        self.include_new_message_into_messaging_area(new_message)

        self.force_focus_on_window_if_there_are_new_messages_from_others([new_message])

    def include_new_message_into_messaging_area(self, message_object):
        self.get_the_background_color_and_anchor_side_for_message(message_object)

        message_type = message_object.get("message_type", "text")
        if message_type == "text":
            self.create_and_include_a_text_label(message_object)
        elif message_type == "smile":
            self.create_and_include_a_smile_label(message_object)
        elif message_type == "picture":
            self.create_and_include_an_image_label(message_object)
        elif message_type == "file":
            self.create_and_include_a_file_label(message_object)

        self.move_scrollbar_to_the_bottom()

    def get_the_background_color_and_anchor_side_for_message(self, message_object):
        if message_object.get("ip_address") == self.ip_address:
            self.message_background = "orange"
            self.message_anchor = tk.E
        else:
            self.message_background = "light sea green"
            self.message_anchor = tk.W

    def create_and_include_a_text_label(self, message_object):
        user_name = message_object.get("user_name", "ghost")
        message = message_object.get("message", "")
        timestamp = message_object.get("timestamp", 0)
        time_to_show = self.get_time_to_show_in_message(timestamp)
        text_to_show = f"{user_name} ({time_to_show}): {message}\n"
        ttk.Label(self.messages_frame.scrollable_frame, text=text_to_show,
                  relief="solid", wraplengt=600, background=self.message_background,
                  font=self.message_text_font,
                  ).pack(anchor=self.message_anchor)

    def create_and_include_a_smile_label(self, message_object):
        smile_type = message_object.get("message")

        file_name = f"smileys/{smile_type}.png"
        file_path = helpers.get_resource_path(file_name)

        smile_file_exists = os.path.isfile(file_path)
        if not smile_file_exists:
            # TODO: return some text or default picture
            print("smile not there", smile_type)
        else:
            photo = ImageTk.PhotoImage(Image.open(file_path))

            smiley_face = tk.Label(self.messages_frame.scrollable_frame, image=photo)
            smiley_face.photo = photo
            smiley_face.pack(anchor=self.message_anchor)

    def create_and_include_an_image_label(self, message_object):
        file_name = message_object.get("message", "")

        if not os.path.isdir(Config.picture_folder):
            os.mkdir(Config.picture_folder)

        file_path = os.path.join(Config.picture_folder, file_name)

        if not os.path.isfile(file_path):
            parameters = {"file_name": file_name}
            response = requests.get(Config.API_URL_PICTURE_STORAGE, params=parameters)
            with open(file_path, 'wb') as f:
                f.write(response.content)

        photo = ImageTk.PhotoImage(Image.open(file_path))

        photo_label = tk.Label(self.messages_frame.scrollable_frame, image=photo)
        photo_label.photo = photo
        photo_label.pack(anchor=self.message_anchor)

    def create_and_include_a_file_label(self, message_object):
        user_name = message_object.get("user_name", "ghost")
        file_name = message_object.get("message", "")
        timestamp = message_object.get("timestamp", 0)
        time_to_show = self.get_time_to_show_in_message(timestamp)
        text_to_show = f"{user_name} ({time_to_show}): FILE (click to download) - {file_name}\n"
        file_label = ttk.Label(
            self.messages_frame.scrollable_frame, text=text_to_show,
            relief="solid", wraplengt=600, background=self.message_background,
            font=self.message_text_font, cursor="hand2"
            )
        file_label.pack(anchor=self.message_anchor)

        file_label.bind('<Button-1>', lambda event: self.handle_file_download(file_name))

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

    def is_there_some_new_message_from_somebody_else(self, new_messages):
        is_there_some_new_message_from_somebody_else = False
        for message in new_messages:
            if message.get("ip_address") != self.ip_address:
                is_there_some_new_message_from_somebody_else = True

        return is_there_some_new_message_from_somebody_else

    def get_time_to_show_in_message(self, timestamp):
        if not timestamp or timestamp == 1:
            return "way ago"

        dt_object = datetime.fromtimestamp(timestamp)

        message_is_from_today = helpers.is_date_from_today(dt_object)
        if not message_is_from_today:
            time_to_show = dt_object.strftime('%d. %m. %H:%M')
        else:
            time_to_show = dt_object.strftime('%H:%M')

        return time_to_show

    def handle_problems_when_filling_message_area(self, err):
        # conversation = f"Network error happened, please check internet connection.\nErr: {err}"
        # self.define_text_content(self.messaging_area_text, conversation)
        # self.last_message_timestamp = 0
        print("problems when filling", err)
        print(traceback.format_exc())

    def process_message_from_entry(self):
        message = self.get_text_from_message_entry()

        if not message:
            return self.handle_empty_message()
        else:
            return self.handle_message_sending(message)

    def handle_message_sending(self, message):
        self.clean_message_entry()

        self.message_sending_queue = queue.Queue()
        actions.MessageSending(
            queue=self.message_sending_queue,
            user_name=self.user_name,
            message=message
        ).start()
        self.parent.after(100, self.process_queue_for_message_sending)

    def process_queue_for_message_sending(self):
        try:
            msg = self.message_sending_queue.get(0)
            success = msg["success"]
            if not success:
                # TODO: could input the message back into the message entry
                reason = msg["reason"]
                self.dialogs.sending_message_problem(reason)
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

    def block_support(self):
        message = "You thought it is so easy?"
        title = "Blocking support"
        colour = "red"
        font_size = 25
        geometry = "400x100"
        self.show_message_on_top(on_top_window=self.support_window, message=message, colour=colour,
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

    def handle_empty_message(self):
        title = "No empty messages!"
        message = "Sending empty messages is not cool. You would not send empty envelopes either."
        colour = "red"
        font_size = 15
        geometry = "750x100"
        self.show_message_on_top(on_top_window=self.support_window, message=message, colour=colour,
                                 font_size=font_size, title=title, geometry=geometry)

    def change_name(self):
        new_name = self.dialogs.get_new_name(self.user_name)

        if new_name:
            self.user_name = new_name
            self.dialogs.name_change_successful()
        else:
            if new_name == "":
                self.dialogs.name_change_empty_name()
            elif new_name is None:
                self.dialogs.name_change_cancelling()

    def move_scrollbar_to_the_bottom(self):
        self.messages_frame.canvas.update_idletasks()
        self.messages_frame.canvas.yview_moveto(1)

    def force_focus_on_window_if_there_are_new_messages_from_others(self, new_messages):
        if self.is_there_some_new_message_from_somebody_else(new_messages):
            print("focusing hard")
            self.parent.after(1, lambda: self.support_window.focus_force())
            self.support_window.focus_force()

    def get_text_from_message_entry(self):
        return self.message_entry.get()

    def clean_message_entry(self):
        self.message_entry.delete(0, "end")

    def place_the_window_to_the_center_of_the_screen(self, window):
        self.parent.parent.eval(f'tk::PlaceWindow {str(window)} center')
