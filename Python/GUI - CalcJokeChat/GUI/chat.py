import os
import requests
import time
import traceback
import re
from datetime import datetime
import urllib.request
from PIL import ImageTk, Image

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

from config import Config
from helpers import get_resource_path


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

        self.confirmation_sent = False
        self.last_message_timestamp = 0
        self.last_message_timestamp = 1605225600

        self.ip_address = self.get_ip_address()

        self.user_name = Config.NAME

        # Needed for the destroyment of infinite checking og messages
        self.after_loop_id = ""

        self.message_text_font = ("Helvetica", 16)
        self.message_background = "orange"
        self.message_anchor = tk.W

        self.button_font = ("Calibri", 20, "bold")
        self.button_border = 5
        self.button_rel_x = 0.75
        self.button_rel_width = 0.2
        self.button_rel_height = 0.1

    @staticmethod
    def get_ip_address():
        response = requests.get(Config.API_URL_IP)
        ip_address_json = response.json()
        return ip_address_json["ip_address"]

    def on_destroy(self):
        print("Cancel, reset and destroy")
        # Making sure the after() function is not called anymore on the background
        self.parent.after_cancel(self.after_loop_id)

        # So that when opening the window again, all messages will be shown,
        #   even when no new messages come
        self.last_message_timestamp = 0

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

        self.update_messaging_area()

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
            file_path = get_resource_path(file_name)

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
        print("label clicked", smile_type)
        self.send_smile(smile_type)

    def handle_picture_sending_dialog(self):
        picture_path = filedialog.askopenfilename(parent=self.support_window)
        print("picture_path", picture_path)
        if not picture_path:
            return

        picture_name = os.path.basename(picture_path)

        if not os.path.isdir(Config.picture_folder):
            os.mkdir(Config.picture_folder)

        picture_save_path = os.path.join(Config.picture_folder, picture_name)

        self.transform_picture_to_max_pixels_size_and_save_it(
            picture_path, picture_save_path)

        file_name_saved = self.upload_picture_to_server(picture_save_path)

        self.send_picture(file_name_saved)

        if file_name_saved != picture_name:
            new_picture_save_path = os.path.join(Config.picture_folder, file_name_saved)
            os.rename(picture_save_path, new_picture_save_path)

        self.confirm_file_successfully_sent(picture_name)

    def confirm_file_successfully_sent(self, file_name):
        title = "Upload finished."
        message = f"File upload of '{file_name}' finished!"
        messagebox.showinfo(title, message, parent=self.support_window)

    @staticmethod
    def transform_picture_to_max_pixels_size_and_save_it(picture_path, picture_save_path):
        max_pixels_size = Config.pictures_max_pixels_size
        orig_image = Image.open(picture_path)
        x_size, y_size = orig_image.size
        max_size = max(x_size, y_size)

        picture_needs_to_be_reduced = max_size > max_pixels_size
        if picture_needs_to_be_reduced:
            if x_size >= y_size:
                ratio = (max_pixels_size / x_size)
                new_x = max_pixels_size
                new_y = int(y_size * ratio)
            else:
                ratio = (max_pixels_size / y_size)
                new_y = max_pixels_size
                new_x = int(x_size * ratio)
            im2 = orig_image.resize((new_x, new_y), Image.BICUBIC)
            im2.save(picture_save_path)
        else:
            orig_image.save(picture_save_path)

    def upload_picture_to_server(self, file_path):
        with open(file_path, 'rb') as file:
            response = requests.post(Config.API_URL_PICTURE_STORAGE, files={'file': file})
        file_name_saved = response.json().get("file_name")
        return file_name_saved

    def handle_file_sending_dialog(self):
        file_path = filedialog.askopenfilename(parent=self.support_window)
        if not file_path:
            return

        file_name_saved = self.upload_file_to_server(file_path)

        self.send_file(file_name_saved)

        file_name = os.path.basename(file_path)
        self.confirm_file_successfully_sent(file_name)

    def upload_file_to_server(self, file_path):
        with open(file_path, 'rb') as file:
            response = requests.post(Config.API_URL_FILE_STORAGE, files={'file': file})
        file_name_saved = response.json().get("file_name")
        return file_name_saved

    def update_messaging_area(self):
        self.call_the_message_updating_function_infinitely()

        try:
            self.update_chat_messages()
        except Exception as err:
            self.handle_problems_when_filling_message_area(err)

    def call_the_message_updating_function_infinitely(self):
        self.after_loop_id = self.parent.after(
            Config.chat_refresh_time_in_ms, self.update_messaging_area)
        print("self.after_loop_id", self.after_loop_id)

    def update_chat_messages(self):
        new_chat_messages = self.get_new_chat_messages()

        if new_chat_messages:
            self.last_message_timestamp = new_chat_messages[-1]["timestamp"]

            self.include_new_messages_into_messaging_area(new_chat_messages)

            self.force_focus_on_window_if_there_are_new_messages_from_others(new_chat_messages)

    def get_new_chat_messages(self):
        # TODO: somehow handle the case of timeout (gracefully, so user does not even notice)
        parameters = {
            "chat_name": Config.CHAT_NAME,
            "last_message_timestamp": self.last_message_timestamp,
            "max_result_size": Config.how_many_messages_to_load_at_startup
        }
        response = requests.get(Config.API_URL_CHAT, params=parameters, timeout=1)
        new_chat_messages = response.json()

        print("new_chat_messages", new_chat_messages)
        return new_chat_messages

    def include_new_messages_into_messaging_area(self, chat_messages):
        for message_object in chat_messages:
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
        file_path = get_resource_path(file_name)

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
        if not self.should_the_file_really_be_downloaded(file_name):
            return

        if not os.path.isdir(Config.download_folder):
            os.mkdir(Config.download_folder)

        parameters = {"file_name": file_name}

        response = requests.get(Config.API_URL_FILE_STORAGE, params=parameters)

        file_name = self.remove_timestamp_and_underscore_from_beginning(file_name)
        file_path_to_save = os.path.join(Config.download_folder, file_name)
        with open(file_path_to_save, 'wb') as downlod_file:
            downlod_file.write(response.content)

        self.confirm_file_downloaded_successfully(file_path_to_save)

    @staticmethod
    def remove_timestamp_and_underscore_from_beginning(file_name):
        pattern = r"^\d{10}_"
        pattern_is_matching = re.match(pattern, file_name)
        if pattern_is_matching:
            characters_to_delete = len(pattern_is_matching.group())
            return file_name[characters_to_delete:]
        else:
            return file_name

    def confirm_file_downloaded_successfully(self, file_path_to_save):
        title = "Download finished."
        message = f"File downloaded as '{file_path_to_save}' in the 'download' folder."
        messagebox.showinfo(title, message, parent=self.support_window)

    def should_the_file_really_be_downloaded(self, file_name):
        title = 'Get the file'
        question = f'Do you really want to download the file "{file_name}"?'
        should_download_the_file = messagebox.askquestion(
            title, question, icon='warning', parent=self.support_window)

        return should_download_the_file == "yes"

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

        message_is_from_today = self.is_date_from_today(dt_object)
        if not message_is_from_today:
            time_to_show = dt_object.strftime('%d. %m. %H:%M')
        else:
            time_to_show = dt_object.strftime('%H:%M')

        return time_to_show

    @staticmethod
    def is_date_from_today(dt_object):
        today_dt_object = datetime.now()
        today_morning = datetime(year=today_dt_object.year, month=today_dt_object.month,
                                 day=today_dt_object.day, hour=0, second=0)
        message_is_from_today = today_morning < dt_object
        return message_is_from_today

    def handle_problems_when_filling_message_area(self, err):
        # conversation = f"Network error happened, please check internet connection.\nErr: {err}"
        # self.define_text_content(self.messaging_area_text, conversation)
        # self.last_message_timestamp = 0
        print("problems when filling", err)
        print(traceback.format_exc())

    def process_message_from_entry(self):
        message = self.get_text_from_message_entry()
        print(message)

        if not message:
            return self.handle_empty_message()
        else:
            return self.send_message(message)

    def send_message(self, message):
        self.send_chat_data(message_type="text", message=message)

        self.clean_message_entry()

    def send_smile(self, smile_type):
        self.send_chat_data(message_type="smile", message=smile_type)

    def send_picture(self, picture_name):
        self.send_chat_data(message_type="picture", message=picture_name)

    def send_file(self, file_name):
        self.send_chat_data(message_type="file", message=file_name)

    def send_chat_data(self, message_type, message):
        data = {
            "message_type": message_type,
            "user_name": self.user_name,
            "message": message,
            "timestamp": time.time(),
            "details": ""
        }
        data_to_send = {"chat_name": Config.CHAT_NAME, "data": data}

        try:
            requests.post(Config.API_URL_CHAT, json=data_to_send)
        except Exception as err:
            self.inform_about_message_sending_problem(err)
            return

    def get_latest_update(self):
        if not self.should_the_latest_version_really_be_downloaded():
            return

        self.inform_about_downloading_start()

        try:
            timestamp = int(time.time())
            path_where_to_save_it = f"Casio_fx-85_CE_X_latest_{timestamp}.exe"

            self.download_latest_update(path_where_to_save_it)
            self.inform_about_downloading_finish(path_where_to_save_it)
        except Exception as err:
            self.inform_about_downloading_problem(err)

    def should_the_latest_version_really_be_downloaded(self):
        last_update = self.get_the_time_of_last_update()
        title = 'Get latest version'
        question = f'Last update released {last_update}. Do you really want to download it?'
        should_get_latest_version = messagebox.askquestion(
            title, question, icon='warning', parent=self.support_window)

        return should_get_latest_version == "yes"

    @staticmethod
    def get_the_time_of_last_update():
        try:
            response = requests.get(Config.API_URL_LAST_UPDATE)
            last_update = response.json()
        except Exception as err:
            return f"Error when finding out. Err: {err}"

        last_update_ts = last_update.get("timestamp", 0)
        dt_object = datetime.fromtimestamp(last_update_ts)
        time_to_show = dt_object.strftime('%d. %m. %Y at %H:%M:%S')
        return time_to_show

    @staticmethod
    def download_latest_update(path_where_to_save_it):
        urllib.request.urlretrieve(Config.latest_version_url, path_where_to_save_it)

    def inform_about_downloading_start(self):
        title = "Download will start after clicking OK. Be patient."
        message = ("Please click OK and then do not click anything, "
                   "the download will block everything else.")
        messagebox.showinfo(title, message, parent=self.support_window)

    def inform_about_downloading_finish(self, path_where_file_was_saved):
        title = "Download finished!"
        message = ("New file is located at the same directory as the current one. "
                   f"Name: {path_where_file_was_saved}.")
        messagebox.showinfo(title, message, parent=self.support_window)

    def inform_about_downloading_problem(self, err):
        title = "Download failed!"
        message = ("We are sorry, but download failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.support_window)

    def inform_about_message_sending_problem(self, err):
        title = "Impossible to send message!"
        message = ("We are sorry, sending the message failed for some reason. "
                   f"Try that again. Err: {err}")
        messagebox.showinfo(title, message, parent=self.support_window)

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

    # Helper function to fill a text component with a content in a safe way
    # Possible modes: "rewrite" - fill it completely from the scratch,
    #   "append" - just appending the specified content to already existing one
    @staticmethod
    def define_text_content(text_component, content_to_fill, mode="rewrite"):
        text_component["state"] = "normal"  # enabling to manipulate the content
        if mode == "rewrite":
            text_component.delete("1.0", "end")  # deleting the whole previous content
        text_component.insert("insert", content_to_fill)  # inserting completely new content
        text_component["state"] = "disabled"  # disabling the content for user manipulation

    def change_name(self):
        question = f"Your current name is \"{self.user_name}\". What should be your new name?"
        new_name = simpledialog.askstring("New name", question, parent=self.parent)
        print(new_name)

        if new_name:
            self.user_name = new_name
            self.inform_about_successful_name_change()
        else:
            if new_name == "":
                self.inform_about_empty_name_when_changing()
            elif new_name is None:
                self.inform_about_cancelling_the_name_change()

    def inform_about_successful_name_change(self):
        title = "Name changed!"
        message = "Your name was changed. Have fun with your new identity!"
        messagebox.showinfo(title, message, parent=self.support_window)

    def inform_about_empty_name_when_changing(self):
        title = "No empty names!"
        message = "Empty names are not allowed. Who would then recognize you?"
        messagebox.showinfo(title, message, parent=self.support_window)

    def inform_about_cancelling_the_name_change(self):
        title = "Out of ideas?"
        message = "Did not come up with a good name? Try looking at the calendar."
        messagebox.showinfo(title, message, parent=self.support_window)

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
