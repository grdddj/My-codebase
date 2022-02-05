import time
import threading
import json
from datetime import datetime

import websocket
import requests

import tkinter as tk
from tkinter import ttk


class Config:
    NAME = "User"
    CHAT_NAME = "chat123"

    SERVER_IP = "123.456.789.0"
    API_PORT = 5678

    SERVER_AND_PORT = f"http://{SERVER_IP}:{API_PORT}"
    API_URL_CHAT = f"{SERVER_AND_PORT}/v1/chat"
    API_URL_IP = f"{SERVER_AND_PORT}/v1/ip_address"

    WEBSOCKET_PORT = 6789
    MESSAGES_WEBSOCKET_URL = f"ws://{SERVER_IP}:{WEBSOCKET_PORT}"

    how_many_messages_to_load_at_startup = 10


class ScrollableFrameForMessages(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)

        # TODO: could request older messages automatically when the scrollbar
        #   would be at the top
        scrollbar = tk.Scrollbar(
            self, orient="vertical", cursor="hand2", command=self.canvas.yview
        )
        scrollbar.config(width=50)
        scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # There is a limit of labels that can accomodate to a tkinter Canvas (around 315)
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", self.adjust_scrolling_region)
        self.canvas.bind("<Configure>", self.adjust_frame_width)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        amount_of_units = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(amount_of_units, "units")

    def adjust_frame_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def adjust_scrolling_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class SupportWindow:
    def __init__(self):
        self.support_window = tk.Tk()

        self.ip_address = get_ip_address()

        self.user_name = Config.NAME

        self.width_of_chat_part = 1.0

        # TODO: create some error handling, when the connection goes down
        # Probably an after() loop here, to check the connection and if down,
        #   recreate it and recreate the message sending object
        self.ws = websocket.create_connection(Config.MESSAGES_WEBSOCKET_URL)

        self.show_support_window()

        self.support_window.mainloop()

    def on_destroy(self):
        # The message getting thread in the background must be killed
        self.getting_message_data_thread.stop()

        # To be sure the stop event is processed, before closing the WS
        time.sleep(0.1)

        self.ws.close()

        self.support_window.destroy()

    def show_support_window(self):
        self.support_window.title("Support")
        # self.support_window.state("zoomed")
        self.support_window.geometry("600x600")

        # Destroying the component is connected with cleaning logic
        self.support_window.protocol("WM_DELETE_WINDOW", self.on_destroy)

        messaging_area = tk.Frame(self.support_window, bg="yellow", bd=10)
        messaging_area.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.messages_frame = ScrollableFrameForMessages(messaging_area)
        self.messages_frame.place(
            relx=0, rely=0, relheight=0.87, relwidth=self.width_of_chat_part
        )

        self.is_other_writing_entry = tk.Entry(
            self.support_window,
            bg="light sea green",
            disabledbackground="light sea green",
            disabledforeground="black",
            font=("Calibri", 7),
            bd=5,
            state="disabled",
        )
        self.is_other_writing_entry.place(
            relx=0, rely=0.87, relheight=0.05, relwidth=self.width_of_chat_part
        )

        self.message_in_entry = tk.StringVar()
        self.message_in_entry.trace("w", self.handle_change_in_message_entry_text)

        self.message_entry = tk.Entry(
            self.support_window,
            textvariable=self.message_in_entry,
            bg="orange",
            font=("Calibri", 8),
            bd=5,
        )
        self.message_entry.place(
            relx=0, rely=0.92, relheight=0.08, relwidth=self.width_of_chat_part
        )
        self.message_entry.focus_set()
        self.message_entry.bind(
            "<Return>", (lambda event: self.process_message_from_entry())
        )

        self.start_getting_messages_in_the_background()

    def start_getting_messages_in_the_background(self):
        self.getting_message_data_thread = GettingMessageData(parent=self)
        self.getting_message_data_thread.start()

    def handle_change_in_message_entry_text(self, *args):
        message = self.get_text_from_message_entry()
        self.send_message_entry_to_websocket(message)

    def send_message_entry_to_websocket(self, message):
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

        if message:
            return self.handle_message_sending(message)

    def handle_message_sending(self, message):
        self.clean_message_entry()
        self.focus_on_message_entry()

        MessageSending(
            ws=self.ws,
            user_name=self.user_name,
            ip_address=self.ip_address,
            message=message,
            answer_to_message="",
        ).start()

    def get_text_from_message_entry(self):
        return self.message_in_entry.get()

    def clean_message_entry(self):
        self.message_in_entry.set("")

    def focus_on_message_entry(self):
        self.message_entry.focus()


class ActionInDifferentThread(threading.Thread):
    def __init__(self, ws=None, user_name="", ip_address=""):
        threading.Thread.__init__(self)
        self.ws = ws
        self.user_name = user_name
        self.ip_address = ip_address

    def run(self):
        self.action_to_be_done()

    def action_to_be_done(self):
        print("WILL BE IMPLEMENTED BY THE SUBCLASSES")

    def send_message_through_websocket_to_all_clients(self, message_data):
        message_data["ip_address"] = self.ip_address
        json_message_data = json.dumps(message_data)

        self.ws.send(json_message_data)

    def send_chat_data(self, message_type, message, answer_to_message=""):
        message_data = {
            "message_type": message_type,
            "user_name": self.user_name,
            "message": message,
            "answer_to_message": answer_to_message,
            "timestamp": time.time(),
            "details": "",
        }

        self.send_message_through_websocket_to_all_clients(message_data)

        data_to_send = {"chat_name": Config.CHAT_NAME, "data": message_data}

        requests.post(Config.API_URL_CHAT, json=data_to_send)


class MessageSending(ActionInDifferentThread):
    def __init__(self, ws, user_name, message, ip_address, answer_to_message):
        ActionInDifferentThread.__init__(self, ws, user_name, ip_address)
        self.message = message
        self.answer_to_message = answer_to_message

    def action_to_be_done(self):
        self.send_chat_data(
            message_type="text",
            message=self.message,
            answer_to_message=self.answer_to_message,
        )


class GettingMessageData(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)

        self.parent = parent

        self.ip_address = get_ip_address()

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
            "max_result_size": Config.how_many_messages_to_load_at_startup,
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

        answer_to_part = (
            f"Answer to: {answer_to_message}\n\n" if answer_to_message else ""
        )

        text_to_show = f"{answer_to_part}{user_name} ({time_to_show})\n{message}\n"

        text_label = ttk.Label(
            self.parent.messages_frame.scrollable_frame,
            text=text_to_show,
            relief="solid",
            wraplengt=600,
            background=self.message_background,
            font=self.message_text_font,
            cursor="hand2",
        )
        text_label.pack(anchor=self.message_anchor)

    def get_time_to_show_in_message(self, timestamp):
        if not timestamp or timestamp == 1:
            return "way ago"

        dt_object = datetime.fromtimestamp(timestamp)

        message_is_from_today = is_date_from_today(dt_object)
        if not message_is_from_today:
            time_to_show = dt_object.strftime("%d. %m. %H:%M")
        else:
            time_to_show = dt_object.strftime("%H:%M")

        return time_to_show

    def handle_update_from_ws(self, message_object):
        message_type = message_object.get("message_type", "")
        if message_type == "entry_update":
            self.update_is_other_writing_entry(message_object)

    def update_is_other_writing_entry(self, message_object):
        ip_address = message_object.get("ip_address", "")
        if ip_address != self.ip_address:
            message = message_object.get("message", "")
            define_entry_content(self.parent.is_other_writing_entry, message)

    def force_focus_on_window(self):
        self.parent.support_window.focus_force()

    def move_scrollbar_to_the_bottom(self):
        self.parent.messages_frame.canvas.update_idletasks()
        self.parent.messages_frame.canvas.yview_moveto(1)


def get_ip_address():
    response = requests.get(Config.API_URL_IP)
    ip_address_json = response.json()
    return ip_address_json["ip_address"]


def is_date_from_today(dt_object):
    today_dt_object = datetime.now()
    today_morning = datetime(
        year=today_dt_object.year,
        month=today_dt_object.month,
        day=today_dt_object.day,
        hour=0,
        second=0,
    )
    message_is_from_today = today_morning < dt_object
    return message_is_from_today


def define_entry_content(entry_component, content_to_fill):
    entry_component["state"] = "normal"
    entry_component.delete(0, "end")
    entry_component.insert(0, content_to_fill)
    entry_component["state"] = "disabled"


if __name__ == "__main__":
    assert (
        Config.SERVER_IP != "123.456.789.0"
    ), "Please input a valid SERVER_IP in Config!"
    SupportWindow()
