import requests
import time
from datetime import datetime
import urllib.request

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

from config import Config


class SupportWindow:
    def __init__(self, parent):
        self.parent = parent

        self.confirmation_sent = False
        self.last_message_timestamp = 0

        self.user_name = Config.NAME

        # Needed for the destroyment of infinite checking og messages
        self.after_loop_id = ""

        self.button_font = ("Calibri", 20, "bold")
        self.button_border = 5
        self.button_rel_x = 0.75
        self.button_rel_width = 0.2
        self.button_rel_height = 0.1

    def on_destroy(self):
        print("Destroy")
        # Making sure the after() function is not called anymore on the background
        self.parent.after_cancel(self.after_loop_id)

        # So that when opening the window again, all messages will be shown,
        #   even when no new messages come
        self.last_message_timestamp = 0

    def show_support_window(self):
        self.support_window = tk.Toplevel(self.parent)
        self.support_window.title("Support")
        self.support_window.state("zoomed")

        # Destroying the component is connected with cleaning logic
        self.support_window.bind("<Destroy>", (lambda event: self.on_destroy()))

        messaging_area = tk.Frame(self.support_window, bg="yellow", bd=10)
        messaging_area.place(relx=0, rely=0, relwidth=1, relheight=1)

        scrollbar = tk.Scrollbar(messaging_area)
        scrollbar.place(relx=0.67, rely=0, relheight=0.87, relwidth=0.03)

        self.messaging_area_text = tk.Text(messaging_area, bg="yellow", font=("Calibri", 15), bd=4,
                                           state="disabled", yscrollcommand=scrollbar.set)
        self.messaging_area_text.place(relx=0, rely=0, relheight=0.87, relwidth=0.67)

        scrollbar.config(command=self.messaging_area_text.yview)

        self.message_entry = tk.Entry(self.support_window, bg="orange", font=("Calibri", 25), bd=5)
        self.message_entry.place(relx=0, rely=0.88, relheight=0.1, relwidth=0.7)
        self.message_entry.bind("<Return>", (lambda event: self.process_message_from_entry()))

        message_sending_button = tk.Button(self.support_window, text="Send question", bg="grey",
                                           font=self.button_font, bd=self.button_border,
                                           command=self.process_message_from_entry)
        message_sending_button.place(relx=self.button_rel_x,
                                     rely=0.88,
                                     relheight=self.button_rel_height,
                                     relwidth=self.button_rel_width)

        change_name_button = tk.Button(self.support_window, text="Change name",
                                       bg="orange", font=self.button_font, bd=self.button_border,
                                       command=self.change_name)
        change_name_button.place(relx=self.button_rel_x,
                                 rely=0.35,
                                 relheight=self.button_rel_height,
                                 relwidth=self.button_rel_width)

        download_latest_version_button = tk.Button(self.support_window, text="Get latest version",
                                                   bg="green", font=self.button_font,
                                                   bd=self.button_border,
                                                   command=self.get_latest_update)
        download_latest_version_button.place(relx=self.button_rel_x,
                                             rely=0.20,
                                             relheight=self.button_rel_height,
                                             relwidth=self.button_rel_width)

        block_support_button = tk.Button(self.support_window, text="Block support",
                                         bg="red", bd=self.button_border,
                                         font=self.button_font, command=self.block_support)
        block_support_button.place(relx=self.button_rel_x,
                                   rely=0.05,
                                   relheight=self.button_rel_height,
                                   relwidth=self.button_rel_width)

        # what_is_new_button - fetch from web on init and timestamp it

        self.update_messaging_area()

    def update_messaging_area(self):
        self.call_the_message_updating_function_infinitely()

        try:
            self.update_chat_messages()
        except Exception as err:
            self.handle_problems_when_filling_message_area(err)

    def call_the_message_updating_function_infinitely(self):
        self.after_loop_id = self.parent.after(Config.chat_refresh_time, self.update_messaging_area)
        print("self.after_loop_id", self.after_loop_id)

    def update_chat_messages(self):
        new_chat_messages = self.get_new_chat_messages()

        # Checking the amount of new messages, and if messages come from somebody else
        #   so that we are notified
        if new_chat_messages:
            self.last_message_timestamp = new_chat_messages[-1]["timestamp"]

            # Creating conversation string to be shown
            # TODO: each message could be a label on its own
            # The one sent by us on right and others on left (as on Messenger)
            self.include_new_messages_into_messaging_area(new_chat_messages)

            self.force_focus_on_window_if_there_are_new_messages_from_others(new_chat_messages)

    def get_new_chat_messages(self):
        # TODO: somehow handle the case of timeout (gracefully, so user does not even notice)
        parameters = {
            "chat_name": Config.CHAT_NAME,
            "last_message_timestamp": self.last_message_timestamp
        }
        response = requests.get(Config.API_URL_CHAT, params=parameters, timeout=1)
        new_chat_messages = response.json()

        print("new_chat_messages", new_chat_messages)
        return new_chat_messages

    def include_new_messages_into_messaging_area(self, chat_messages):
        conversation_text = self.create_conversation_text_from_messages(chat_messages)
        self.append_conversation_text_into_messaging_area(conversation_text)
        self.move_scrollbar_to_the_bottom()

    def create_conversation_text_from_messages(self, chat_messages):
        conversation_text = ""
        for entry in chat_messages:
            name = entry.get("user_name", "ghost")
            message = entry.get("message", "")
            timestamp = entry.get("timestamp", 0)

            time_to_show = self.get_time_to_show_in_message(timestamp)

            string_to_add = f"{name} ({time_to_show}): {message}\n"
            conversation_text = conversation_text + string_to_add

        return conversation_text

    def is_there_some_new_message_from_somebody_else(self, new_messages):
        is_there_some_new_message_from_somebody_else = False
        for message in new_messages:
            if message.get("user_name") != self.user_name:
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

    def process_message_from_entry(self):
        message = self.get_text_from_message_entry()
        print(message)

        if not message:
            return self.handle_empty_message()
        else:
            return self.send_message(message)

    def send_message(self, message):
        data = {
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

        self.clean_message_entry()

        self.show_confirmation_message()

    def get_latest_update(self):
        if self.should_the_latest_version_really_be_downloaded():
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
        should_get_latest_version = messagebox.askquestion(title, question, icon='warning')

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

    @staticmethod
    def inform_about_downloading_start():
        title = "Download will start after clicking OK. Be patient."
        message = "Please click OK and then do not click anything, the download will block everything else."
        messagebox.showinfo(title, message)

    @staticmethod
    def inform_about_downloading_finish(path_where_file_was_saved):
        title = "Download finished!"
        message = f"New file is located at the same directory as the current one. Name: {path_where_file_was_saved}."
        messagebox.showinfo(title, message)

    @staticmethod
    def inform_about_downloading_problem(err):
        title = "Download failed!"
        message = f"We are sorry, but download failed for some reason. Try that again. Err: {err}"
        messagebox.showinfo(title, message)

    @staticmethod
    def inform_about_message_sending_problem(err):
        title = "Impossible to send message!"
        message = f"We are sorry, sending the message failed for some reason. Try that again. Err: {err}"
        messagebox.showinfo(title, message)

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

    def show_confirmation_message(self):
        if not self.confirmation_sent:
            title = "Question noted down"
            message = "Your question saved. Support usually responds within 24 hours."
            colour = "orange"
            font_size = 15
            geometry = "600x100"
            self.show_message_on_top(on_top_window=self.support_window, message=message,
                                     colour=colour, font_size=font_size,
                                     title=title, geometry=geometry)

            self.confirmation_sent = True

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

    @staticmethod
    def inform_about_successful_name_change():
        title = "Name changed!"
        message = "Your name was changed. Have fun with your new identity!"
        messagebox.showinfo(title, message)

    @staticmethod
    def inform_about_empty_name_when_changing():
        title = "No empty names!"
        message = "Empty names are not allowed. Who would then recognize you?"
        messagebox.showinfo(title, message)

    @staticmethod
    def inform_about_cancelling_the_name_change():
        title = "Out of ideas?"
        message = "Did not come up with a good name? Try looking at the calendar."
        messagebox.showinfo(title, message)

    def move_scrollbar_to_the_bottom(self):
        self.messaging_area_text.yview_moveto(1)

    def force_focus_on_window_if_there_are_new_messages_from_others(self, new_messages):
        if self.is_there_some_new_message_from_somebody_else(new_messages):
            print("focusing hard")
            self.parent.after(1, lambda: self.support_window.focus_force())
            # self.support_window.focus_force()

    def append_conversation_text_into_messaging_area(self, conversation_text):
        self.define_text_content(self.messaging_area_text, conversation_text, mode="append")

    def get_text_from_message_entry(self):
        return self.message_entry.get()

    def clean_message_entry(self):
        self.message_entry.delete(0, "end")

    def place_the_window_to_the_center_of_the_screen(self, window):
        self.parent.parent.eval(f'tk::PlaceWindow {str(window)} center')
