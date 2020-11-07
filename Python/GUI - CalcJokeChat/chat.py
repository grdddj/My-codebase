import os
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
        self.number_of_messages_known = 0

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
        self.number_of_messages_known = 0

    def show(self):
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

    def call_the_message_updating_function_infinitely(self):
        self.after_loop_id = self.parent.after(Config.chat_refresh_time, self.update_messaging_area)
        print("self.after_loop_id", self.after_loop_id)

    def update_messaging_area(self):
        self.call_the_message_updating_function_infinitely()

        try:
            chat_messages = self.get_chat_messages()

            # Checking the amount of new messages, and if messages come from somebody else
            #   so that we are notified
            number_of_messages = len(chat_messages)
            there_are_new_messages = number_of_messages != self.number_of_messages_known
            if there_are_new_messages:
                new_messages = chat_messages[self.number_of_messages_known-1:]
                self.number_of_messages_known = number_of_messages

                # Creating conversation string to be shown
                # TODO: each message could be a label on its own
                # The one sent by us on right and others on left (as on Messenger)
                # TODO: process only the new messages, and the "append" filling
                self.fill_messaging_area_with_all_messages(chat_messages)

                if self.is_there_some_new_message_from_somebody_else(new_messages):
                    self.support_window.focus_force()
        except Exception as err:
            self.handle_problems_when_filling_message_area(err)

    def get_chat_messages(self):
        response = requests.get(Config.API_URL, timeout=1)
        content = response.json()

        # TODO: get only the messages if there are some new, not to send so much data in vain
        #   send the number of messages we have and server will compare it, and maybe send the data
        # IF the get is supporting parameters - if not, we will use POST
        chat_messages = content.get(Config.CHAT_KEY, [])

        return chat_messages

    def fill_messaging_area_with_all_messages(self, chat_messages):
        conversation = ""
        for entry in chat_messages:
            name = entry.get("name", "ghost")
            message = entry.get("message", "")
            timestamp = entry.get("timestamp", 0)

            time_to_show = self.get_time_to_show_in_message(timestamp)

            string_to_add = f"{name} ({time_to_show}): {message}\n"
            conversation = conversation + string_to_add

        self.define_text_content(self.messaging_area_text, conversation)
        self.messaging_area_text.yview_moveto(1)

    def is_there_some_new_message_from_somebody_else(self, new_messages):
        is_there_some_new_message_from_somebody_else = False
        for message in new_messages:
            if message.get("name") != self.user_name:
                is_there_some_new_message_from_somebody_else = True

        return is_there_some_new_message_from_somebody_else

    def get_time_to_show_in_message(self, timestamp):
        if not timestamp:
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
        conversation = f"Network error happened, please check internet connection.\nErr: {err}"
        self.define_text_content(self.messaging_area_text, conversation)
        self.number_of_messages_known = 0

    def process_message_from_entry(self):
        message = self.message_entry.get()
        print(message)

        if not message:
            return self.handle_empty_message()
        else:
            return self.send_message(message)

    def send_message(self, message):
        self.message_entry.delete(0, "end")

        timestamp = int(time.time())

        data = {"name": self.user_name, "message": message, "timestamp": timestamp}
        data_to_send = {"key_to_save": Config.CHAT_KEY, "data": data}

        try:
            requests.post(Config.API_URL, json=data_to_send)
        except Exception as err:
            self.inform_about_message_sending_problem(err)

        self.show_confirmation_message()

    def get_latest_update(self):
        last_update = self.get_the_time_of_last_update()
        title = 'Get latest version'
        question = f'Last update released {last_update}. Do you really want to download it?'
        should_get_latest_version = messagebox.askquestion(title, question, icon='warning')
        if should_get_latest_version == 'yes':
            self.inform_about_downloading_start()

            try:
                self.download_latest_update()
                self.inform_about_downloading_finish()
            except Exception as err:
                self.inform_about_downloading_problem(err)

    @staticmethod
    def get_the_time_of_last_update():
        response = requests.get(Config.API_URL)
        content = response.json()

        key_to_use = "last_update"
        updates_list = content.get(key_to_use, [])
        if len(updates_list):
            last_update = updates_list[-1]
            last_update_ts = last_update.get("timestamp", 0)
            dt_object = datetime.fromtimestamp(last_update_ts)
            time_to_show = dt_object.strftime('%d. %m. %Y at %H:%M:%S')
            return time_to_show
        else:
            return "Never"

    @staticmethod
    def download_latest_update():
        WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        timestamp = int(time.time())
        file_name = f"Casio_fx-85_CE_X_latest_{timestamp}.exe"
        file_name = os.path.join(WORKING_DIRECTORY, file_name)

        urllib.request.urlretrieve(Config.latest_version_url, file_name)

    @staticmethod
    def inform_about_downloading_start():
        title = "Download will start after clicking OK. Be patient."
        message = "Please click OK and then do not click anything, the download will block everything else."
        messagebox.showinfo(title, message)

    @staticmethod
    def inform_about_downloading_finish():
        title = "Download finished!"
        message = "You can find the new file in the same directory as this one. It will have a unique suffix."
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

        # Placing the window (at least its left top corner) to the center
        self.parent.parent.eval(f'tk::PlaceWindow {str(message_window)} center')

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
            title = "Name changed!"
            message = "Your name was changed. Have fun with your new identity!"
            messagebox.showinfo(title, message)
        else:
            if new_name == "":
                title = "No empty names!"
                message = "Empty names are not allowed. Who would then recognize you?"
                messagebox.showinfo(title, message)
            elif new_name is None:
                title = "Out of ideas?"
                message = "Did not come up with a good name? Try looking at the calendar."
                messagebox.showinfo(title, message)
