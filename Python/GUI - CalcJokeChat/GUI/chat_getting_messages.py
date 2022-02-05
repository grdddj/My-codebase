from typing import Any, Dict, List
import requests
import os
import json
import threading
import traceback
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk
from datetime import datetime

from websocket import WebSocketConnectionClosedException

from config import Config
import helpers
import chat_logger

Message = Dict[str, Any]


class GettingMessageData(threading.Thread):
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)

        self.parent = parent

        self.ip_address = helpers.get_ip_address()

        self.message_text_font = ("Helvetica", 16)
        self.message_background = "orange"
        self.message_anchor = tk.W

        self.log_identifier = "GETTING MESSAGES"

        self._stop_event = threading.Event()

    def stop(self) -> None:
        self.log_info("Stopping the messaging thread")
        self._stop_event.set()

    def is_stopped(self) -> bool:
        return self._stop_event.is_set()

    def run(self) -> None:
        try:
            self.get_recent_messages_from_api_and_render_them()
            self.listen_on_the_websocket_and_render_incoming_messages()
            self.log_info("The messaging thread successfully destroyed")
        except Exception as err:
            print(traceback.format_exc())
            self.log_exception(f"Getting messages exception - {err}")
            raise

    def get_recent_messages_from_api_and_render_them(self) -> None:
        self.log_info("Getting messages from API")
        new_messages = self.get_recent_chat_messages()
        self.log_info(f"Received {len(new_messages)} recent messages from API.")
        for message_obj in new_messages:
            self.process_message_and_include_it_in_frontend(message_obj)

    def listen_on_the_websocket_and_render_incoming_messages(self) -> None:
        self.log_info("Starting to listen on the websocket for messages")

        while True:
            if self.is_stopped():
                self.log_info(
                    "Stop event received. Breaking the websocket listening loop."
                )
                break

            # When the websocket object is closed, the lookup can raise OSError
            try:
                new_message = self.parent.ws.recv()
                if not new_message:
                    self.log_info("Websocket received an empty message. Ignoring")
                    continue

                try:
                    message_obj = json.loads(new_message)
                except json.decoder.JSONDecodeError:
                    self.log_exception(
                        f"Failed to parse websocket message - {new_message}"
                    )
                    self.parent.set_health_check(ok=False)
                    continue

                if "update" in message_obj:
                    self.handle_update_from_ws(message_obj)
                else:
                    self.log_info(f"Websocket received a new message - {new_message}")
                    self.process_message_and_include_it_in_frontend(message_obj)

                self.parent.set_health_check(ok=True)
            except (OSError, WebSocketConnectionClosedException) as err:
                # TODO: could have some defence against a flood with these errors
                # (store a timestamp and log only once per second)
                self.log_error(f"Websocket Close exception - '{err}'")
                self.parent.set_health_check(ok=False)
            except Exception as err:
                self.log_exception(f"Websocket processing exception - {err}")
                self.parent.set_health_check(ok=False)

    def get_recent_chat_messages(self) -> List[Message]:
        parameters = {
            "chat_name": Config.CHAT_NAME,
            "last_message_timestamp": 0,
            "max_result_size": Config.how_many_messages_to_load_at_startup,
        }
        self.log_info(f"Parameters to send to API - {parameters}")
        response = requests.get(Config.API_URL_CHAT, params=parameters)
        new_chat_messages = response.json()

        return new_chat_messages

    def process_message_and_include_it_in_frontend(
        self, message_object: Message
    ) -> None:
        self.get_the_background_color_and_anchor_side_for_message(message_object)

        message_type = message_object.get("message_type", "")
        if message_type == "text":
            self.create_and_include_a_text_label(message_object)
        elif message_type == "smile":
            self.create_and_include_a_smile_label(message_object)
        elif message_type == "picture":
            self.create_and_include_an_image_label(message_object)
        elif message_type == "file":
            self.create_and_include_a_file_label(message_object)
        else:
            self.log_warning(f"Message type not supported - {message_type}")
            return

        self.move_scrollbar_to_the_bottom()
        self.force_focus_on_window()
        self.parent.focus_on_message_entry()

    def get_the_background_color_and_anchor_side_for_message(
        self, message_object: Message
    ) -> None:
        if message_object.get("ip_address") == self.ip_address:
            self.message_background = "orange"
            self.message_anchor = tk.E
        else:
            self.message_background = "light sea green"
            self.message_anchor = tk.W

    def create_and_include_a_text_label(self, message_object: Message) -> None:
        self.log_info(f"Creating text label - {message_object}")
        user_name = message_object.get("user_name", "ghost")
        message = message_object.get("message", "")
        answer_to_message = message_object.get("answer_to_message", "")
        timestamp = message_object.get("timestamp", 0)
        time_to_show = self.get_time_to_show_in_message(timestamp)

        answer_to_part = (
            f"Answer to: {answer_to_message}\n\n" if answer_to_message else ""
        )

        text_to_show = f"{answer_to_part}{user_name} ({time_to_show})\n{message}\n"

        text_label = ttk.Label(
            self.parent.messages_frame.scrollable_frame,
            text=text_to_show,
            relief="solid",
            wraplength=600,
            background=self.message_background,
            font=self.message_text_font,
            cursor="hand2",
        )
        text_label.pack(anchor=self.message_anchor)
        text_label.bind(
            "<Button-1>", lambda event: self.deal_with_asnwer_to(message_object)
        )
        text_label.bind("<Button-3>", lambda event: self.copy_message(message))

    def deal_with_asnwer_to(self, message_object: Message) -> None:
        answer_to_message = message_object.get("message", "")
        self.log_info(f"Answer to clicked - message - '{answer_to_message}'")
        text_to_fill = f"Answer to: {answer_to_message}"
        helpers.define_entry_content(self.parent.answer_to_message_entry, text_to_fill)
        self.parent.show_answer_to_message_cancel_label(show=True)

    def copy_message(self, message: str) -> None:
        self.log_info(f"Message copied - '{message}'")
        helpers.copy_into_clipboard(message)
        self.parent.dialogs.message_copied_into_clipboard(message)

    def create_and_include_a_smile_label(self, message_object: Message) -> None:
        self.log_info(f"Creating smile label - {message_object}")
        smile_type = message_object.get("message")

        file_name = f"smileys/{smile_type}.png"
        file_path = helpers.get_resource_path(file_name)

        smile_file_exists = os.path.isfile(file_path)
        if not smile_file_exists:
            # TODO: return some text or default picture
            self.log_error(f"Smile not there - {smile_type}")
        else:
            photo = ImageTk.PhotoImage(Image.open(file_path))

            smiley_face = tk.Label(
                self.parent.messages_frame.scrollable_frame, image=photo
            )
            smiley_face.photo = photo
            smiley_face.pack(anchor=self.message_anchor)

    def create_and_include_an_image_label(self, message_object: Message) -> None:
        self.log_info(f"Creating image label - {message_object}")
        file_name = message_object.get("message", "")

        if not os.path.isdir(Config.picture_folder):
            os.mkdir(Config.picture_folder)

        file_path = os.path.join(Config.picture_folder, file_name)

        if not os.path.isfile(file_path):
            self.log_info(f"Downloading the picture for the label - {file_path}")
            parameters = {"file_name": file_name}
            response = requests.get(Config.API_URL_PICTURE_STORAGE, params=parameters)
            with open(file_path, "wb") as f:
                f.write(response.content)

        photo = ImageTk.PhotoImage(Image.open(file_path))

        photo_label = tk.Label(self.parent.messages_frame.scrollable_frame, image=photo)
        photo_label.photo = photo
        photo_label.pack(anchor=self.message_anchor)

    def create_and_include_a_file_label(self, message_object: Message) -> None:
        self.log_info(f"Creating file label - {message_object}")
        user_name = message_object.get("user_name", "ghost")
        file_name = message_object.get("message", "")
        timestamp = message_object.get("timestamp", 0)
        time_to_show = self.get_time_to_show_in_message(timestamp)
        text_to_show = (
            f"{user_name} ({time_to_show})\nFILE (click to download)\n{file_name}\n"
        )
        file_label = ttk.Label(
            self.parent.messages_frame.scrollable_frame,
            text=text_to_show,
            relief="solid",
            wraplength=600,
            background=self.message_background,
            font=self.message_text_font,
            cursor="hand2",
        )
        file_label.pack(anchor=self.message_anchor)

        file_label.bind(
            "<Button-1>", lambda event: self.parent.handle_file_download(file_name)
        )

    def get_time_to_show_in_message(self, timestamp: int) -> str:
        if not timestamp or timestamp == 1:
            return "way ago"

        dt_object = datetime.fromtimestamp(timestamp)

        message_is_from_today = helpers.is_date_from_today(dt_object)
        if not message_is_from_today:
            time_to_show = dt_object.strftime("%d. %m. %H:%M")
        else:
            time_to_show = dt_object.strftime("%H:%M")

        return time_to_show

    def handle_update_from_ws(self, message_object: Message) -> None:
        message_type = message_object.get("message_type", "")
        if message_type == "entry_update":
            self.update_is_other_writing_entry(message_object)

    def update_is_other_writing_entry(self, message_object: Message) -> None:
        ip_address = message_object.get("ip_address", "")
        if ip_address != self.ip_address:
            message = message_object.get("message", "")
            helpers.define_entry_content(self.parent.is_other_writing_entry, message)

    def force_focus_on_window(self) -> None:
        self.log_info("Focusing on the support window")
        self.parent.support_window.focus_force()

    def move_scrollbar_to_the_bottom(self) -> None:
        self.log_info("Moving scrollbar to the bottom")
        self.parent.messages_frame.canvas.update_idletasks()
        self.parent.messages_frame.canvas.yview_moveto(1)

    def log_info(self, message: str) -> None:
        chat_logger.info(f"{self.log_identifier} - {message}")

    def log_error(self, message: str) -> None:
        chat_logger.error(f"{self.log_identifier} - {message}")

    def log_warning(self, message: str) -> None:
        chat_logger.warning(f"{self.log_identifier} - {message}")

    def log_exception(self, message: str) -> None:
        chat_logger.exception(f"{self.log_identifier} - {message}")
