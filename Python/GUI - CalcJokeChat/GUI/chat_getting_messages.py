import requests
import os
import json
import threading
import traceback
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk
from datetime import datetime

import websocket
from websocket import WebSocketConnectionClosedException
# websocket.enableTrace(True)

from config import Config
import helpers


class GettingMessageData(threading.Thread):
    def __init__(self, messages_frame, handle_file_download, support_window):
        threading.Thread.__init__(self)

        self.messages_frame = messages_frame
        self.handle_file_download = handle_file_download
        self.support_window = support_window

        self.ip_address = helpers.get_ip_address()

        self.message_text_font = ("Helvetica", 16)
        self.message_background = "orange"
        self.message_anchor = tk.W

    def stop(self):
        print("stopping the background thread")
        self.ws.close()

    def run(self):
        self.get_recent_messages_from_api_and_render_them()
        self.listen_on_the_websocket_and_render_incoming_messages()
        print("end of the 'run' function")

    def get_recent_messages_from_api_and_render_them(self):
        new_messages = self.get_recent_chat_messages()
        for message_obj in new_messages:
            self.process_message_and_include_it_in_frontend(message_obj)

    def listen_on_the_websocket_and_render_incoming_messages(self):
        print("running the ws")
        self.ws = websocket.create_connection(Config.MESSAGES_WEBSOCKET_URL)

        while True:
            # When the websocket object is closed, the lookup can raise OSError
            try:
                new_message = self.ws.recv()
                message_obj = json.loads(new_message)
                self.process_message_and_include_it_in_frontend(message_obj)
            except (OSError, WebSocketConnectionClosedException) as err:
                print("CLOSE exception", err)
                break
            except Exception as err:
                print("exception when getting messages", err)
                print(traceback.format_exc())

    def get_recent_chat_messages(self):
        parameters = {
            "chat_name": Config.CHAT_NAME,
            "last_message_timestamp": 0,
            "max_result_size": Config.how_many_messages_to_load_at_startup
        }
        response = requests.get(Config.API_URL_CHAT, params=parameters)
        new_chat_messages = response.json()

        return new_chat_messages

    def process_message_and_include_it_in_frontend(self, message_object):
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
        self.force_focus_on_window()

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

    def force_focus_on_window(self):
        print("focusing hard")
        self.support_window.focus_force()

    def move_scrollbar_to_the_bottom(self):
        self.messages_frame.canvas.update_idletasks()
        self.messages_frame.canvas.yview_moveto(1)
