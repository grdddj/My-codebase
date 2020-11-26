import requests
import json
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from config import Config
import helpers


class GettingMessageData(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)

        self.parent = parent

        self.ip_address = helpers.get_ip_address()

        self.message_text_font = ("Helvetica", 8)
        self.message_background = "orange"
        self.message_anchor = tk.W

        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self.get_recent_messages_from_api_and_render_them()
        self.listen_on_the_websocket_and_render_incoming_messages()

    def get_recent_messages_from_api_and_render_them(self):
        new_messages = self.get_recent_chat_messages()
        for message_obj in new_messages:
            self.process_message_and_include_it_in_frontend(message_obj)

    def listen_on_the_websocket_and_render_incoming_messages(self):
        while True:
            if self.is_stopped():
                break

            # When the websocket object is closed, the lookup can raise OSError
            try:
                new_message = self.parent.ws.recv()
                if not new_message:
                    continue

                try:
                    message_obj = json.loads(new_message)
                except json.decoder.JSONDecodeError:
                    continue

                if "update" in message_obj:
                    self.handle_update_from_ws(message_obj)
                else:
                    self.process_message_and_include_it_in_frontend(message_obj)
            except Exception:
                pass

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
        message_type = message_object.get("message_type", "")
        if message_type == "text":
            self.get_the_background_color_and_anchor_side_for_message(message_object)
            self.create_and_include_a_text_label(message_object)

            self.move_scrollbar_to_the_bottom()
            self.force_focus_on_window()
            self.parent.focus_on_message_entry()

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
        answer_to_message = message_object.get("answer_to_message", "")
        timestamp = message_object.get("timestamp", 0)
        time_to_show = self.get_time_to_show_in_message(timestamp)

        answer_to_part = f"Answer to: {answer_to_message}\n\n" if answer_to_message else ""

        text_to_show = f"{answer_to_part}{user_name} ({time_to_show})\n{message}\n"

        text_label = ttk.Label(
            self.parent.messages_frame.scrollable_frame, text=text_to_show,
            relief="solid", wraplengt=600, background=self.message_background,
            font=self.message_text_font, cursor="hand2"
        )
        text_label.pack(anchor=self.message_anchor)

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

    def handle_update_from_ws(self, message_object):
        message_type = message_object.get("message_type", "")
        if message_type == "entry_update":
            self.update_is_other_writing_entry(message_object)

    def update_is_other_writing_entry(self, message_object):
        ip_address = message_object.get("ip_address", "")
        if ip_address != self.ip_address:
            message = message_object.get("message", "")
            helpers.define_entry_content(self.parent.is_other_writing_entry, message)

    def force_focus_on_window(self):
        self.parent.support_window.focus_force()

    def move_scrollbar_to_the_bottom(self):
        self.parent.messages_frame.canvas.update_idletasks()
        self.parent.messages_frame.canvas.yview_moveto(1)
