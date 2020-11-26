import time
import queue
import json
import websocket

import tkinter as tk
from tkinter import ttk

from config import Config
import chat_threading_actions as actions
import chat_getting_messages as messages
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
    def __init__(self):
        self.support_window = tk.Tk()

        self.ip_address = helpers.get_ip_address()

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
        self.messages_frame.place(relx=0, rely=0, relheight=0.87, relwidth=self.width_of_chat_part)

        self.is_other_writing_entry = tk.Entry(
            self.support_window, bg="light sea green",
            disabledbackground="light sea green",
            disabledforeground="black",
            font=("Calibri", 7), bd=5, state="disabled"
        )
        self.is_other_writing_entry.place(relx=0, rely=0.87, relheight=0.05, relwidth=self.width_of_chat_part)

        self.message_in_entry = tk.StringVar()
        self.message_in_entry.trace("w", self.handle_change_in_message_entry_text)

        self.message_entry = tk.Entry(
            self.support_window, textvariable=self.message_in_entry,
            bg="orange", font=("Calibri", 8), bd=5)
        self.message_entry.place(relx=0, rely=0.92, relheight=0.08, relwidth=self.width_of_chat_part)
        self.message_entry.focus_set()
        self.message_entry.bind("<Return>", (lambda event: self.process_message_from_entry()))

        self.start_getting_messages_in_the_background()

    def start_getting_messages_in_the_background(self):
        self.getting_message_data_thread = messages.GettingMessageData(
            parent=self
        )
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

        self.message_sending_queue = queue.Queue()
        actions.MessageSending(
            queue=self.message_sending_queue,
            ws=self.ws,
            user_name=self.user_name,
            ip_address=self.ip_address,
            message=message,
            answer_to_message=""
        ).start()

    def get_text_from_message_entry(self):
        return self.message_in_entry.get()

    def clean_message_entry(self):
        self.message_in_entry.set("")

    def focus_on_message_entry(self):
        self.message_entry.focus()


if __name__ == "__main__":
    SupportWindow()
