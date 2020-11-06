import os
import sys
import json
import random
import requests
import time
from datetime import datetime
import urllib.request

import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter import simpledialog

from config import Config

# TODO: "Answer to" functionality
# TODO: Maybe not scroll the scroller down when updating (maybe once in a minute)
#   when the scrollbar is at the bottom currently, do it, otherwise not
# TODO: tell apart the messages of User vs Support - different colours etc.
# TODO: have some spacing between the messages (or right-left side)
# TODO: translation capabilities (like Lorcan's chatbot)
# TODO: allow for sharing pictures and files
# TODO: think about the sizing of the chat - so the words are not cut at the end of line
#   hardcode the window size and limit the characters
# TODO: emoticons
# TODO: thumbs up or other one-click symbol
# TODO: having a mood
# TODO: storing the whole user profile
# TODO: showing if somebody is on/offline
# TODO: websocket!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#   however, not sure how it would work with only one-thread Tkinter
# TODO: creating a better app in PyQt5?
# TODO: move it on git (after cleaning the code)
# TODO: have some kind of build pipeline - on the server with pyinstaller
#   pyinstaller --noconfirm --onefile --windowed --icon "C:/Users/musil/Downloads/Oxygen-Icons.org-Oxygen-Apps-preferences-kcalc-constants.ico" --add-data "D:/Programování/Random programming stuff/jokes.json;."  "D:/Programování/Random programming stuff/calc_oop.py"
# TODO: issue some alerts on there
# TODO: have gifts (for money)
# TODO: implement some points for each message
# TODO: notification about incoming message - glowing of the icon or something like that
#   voice signal - play mp3 or wav, which can be packed together with app
# TODO: "Seen" of the message
# TODO: Show that somebody is typing
# TODO: autocorrect, aka Grammarly
# TODO: machine learning determining the tone of conversation (or topic)
# TODO: predefined answers


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)


# TODO: instantiate as a real object
class Jokes:
    jokes_file = "jokes.json"
    jokes_file_path = resource_path(jokes_file)

    with open(jokes_file_path, 'r', encoding='utf-8') as my_file:
        JOKES = json.load(my_file)


class SupportWindow:
    def __init__(self, parent):
        self.parent = parent

        self.confirmation_sent = False
        self.number_of_messages_known = 0

        self.user_name = Config.NAME

    def show(self):
        self.support_window = tk.Toplevel(self.parent)
        self.support_window.title("Support")
        window_width = 800
        window_height = 600
        self.support_window.geometry("{}x{}".format(window_width, window_height))

        messaging_area = tk.Frame(self.support_window, bg="yellow", bd=10)
        messaging_area.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.scrollbar = tk.Scrollbar(messaging_area)
        self.scrollbar.place(relx=0.97, rely=0, relheight=0.7, relwidth=0.05)

        self.messaging_area_text = tk.Text(messaging_area, bg="yellow", font=("Calibri", 15), bd=4,
                                           state="disabled", yscrollcommand=self.scrollbar.set)
        self.messaging_area_text.place(relx=0, rely=0, relheight=0.7, relwidth=0.97)

        self.scrollbar.config(command=self.messaging_area_text.yview)

        self.message_entry = tk.Entry(self.support_window, bg="orange", font=("Calibri", 15), bd=5)
        self.message_entry.place(relx=0, rely=0.75, relheight=0.1, relwidth=1)
        self.message_entry.bind("<Return>", (lambda event: self.process_message()))

        message_sending_button = tk.Button(self.support_window, text="Send question", bg="grey",
                                           font=("Calibri", 15),
                                           command=self.process_message)
        message_sending_button.place(relx=0.01, rely=0.87, relheight=0.1, relwidth=0.20)

        change_name_button = tk.Button(self.support_window, text="Change name",
                                       bg="orange", font=("Calibri", 15),
                                       command=self.change_name)
        change_name_button.place(relx=0.33, rely=0.87, relheight=0.1, relwidth=0.20)

        download_latest_version_button = tk.Button(self.support_window, text="Get latest version",
                                                   bg="green", font=("Calibri", 15),
                                                   command=self.get_latest_update)
        download_latest_version_button.place(relx=0.55, rely=0.87, relheight=0.1, relwidth=0.20)

        block_support_button = tk.Button(self.support_window, text="Block support", bg="red",
                                         font=("Calibri", 15), command=self.block_support)
        block_support_button.place(relx=0.8, rely=0.87, relheight=0.1, relwidth=0.18)

        self.fill_messaging_area()

    def fill_messaging_area(self):
        try:
            response = requests.get(Config.API_URL)
            content = response.json()

            our_chat = content.get(Config.CHAT_KEY, [])

            # Checking the amount of new messages, and if messages come from somebody else
            #   so that we are notified
            number_of_messages = len(our_chat)
            there_are_new_messages = number_of_messages != self.number_of_messages_known
            if there_are_new_messages:
                new_messages = our_chat[self.number_of_messages_known-1:]
                self.number_of_messages_known = number_of_messages

                is_there_some_message_from_somebody_else = False
                for message in new_messages:
                    if message.get("name") != self.user_name:
                        is_there_some_message_from_somebody_else = True

                if is_there_some_message_from_somebody_else:
                    self.support_window.focus_force()

                # Creating conversation string to be shown
                conversation = ""
                for entry in our_chat:
                    name = entry.get("name", "ghost")
                    message = entry.get("message", "")

                    timestamp = entry.get("timestamp", 0)
                    if timestamp:
                        dt_object = datetime.fromtimestamp(timestamp)

                        today_dt_object = datetime.now()
                        today_morning = datetime(year=today_dt_object.year, month=today_dt_object.month,
                                                 day=today_dt_object.day, hour=0, second=0)
                        message_is_from_today = today_morning < dt_object

                        if not message_is_from_today:
                            time_to_show = dt_object.strftime('%d. %m. %H:%M')
                        else:
                            time_to_show = dt_object.strftime('%H:%M')
                    else:
                        time_to_show = "way ago"

                    str_to_add = f"{name} ({time_to_show}): {message}\n"
                    conversation = conversation + str_to_add

                self.define_text_content(self.messaging_area_text, conversation)
                self.messaging_area_text.yview_moveto(1)
        except Exception as err:
            conversation = f"Network error happened, please check internet connection.\nErr: {err}"
            self.define_text_content(self.messaging_area_text, conversation)
            self.number_of_messages_known = 0

        # TODO: do this only when appending to the discussion list

        # scrollbar_place = scrollbar.get()
        # print("scrollbar_place", scrollbar_place)
        # y_scrollbar = scrollbar_place[1]

        # if y_scrollbar > 0.9:
        #     print("moving scrollbar")
        #     messaging_area_text.yview_moveto(1)
        # else:
        #     messaging_area_text.yview_moveto(y_scrollbar)

        # TODO: find out how to stop this when the Support window is closed
        # root.after_cancel(self._job)
        # WARNING: currently it is spawning another job when the window is reopened
        # TODO: research the destructor of the whole window and functionality
        # widget_class_object.destroy
        after_loop_id = self.parent.after(Config.chat_refresh_time, self.fill_messaging_area)
        print("after_loop_id", after_loop_id)

    def process_message(self):
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
        except Exception as e:
            print("Problem when sending message", e)
            # TODO: show some popup

        self.show_confirmation_message()

    def get_latest_update(self):
        last_update = self.get_the_time_of_last_update()
        title = 'Get latest version'
        question = f'Last update released {last_update}. Do you really want to download it?'
        should_get_latest_version = messagebox.askquestion(title, question, icon='warning')
        if should_get_latest_version == 'yes':
            self.inform_about_downloading_start()

            self.download_latest_update()

            self.inform_about_downloading_finish()
        else:
            pass

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


class CalculatorGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.parent.configure(background="light green")
        self.parent.title("Veronica's Calculator")
        self.parent.geometry("583x379")
        self.parent.resizable(width=False, height=False)

        self.equation = tk.StringVar()
        self.expression = ""

        self.width_of_buttons = 12
        self.height_of_buttons = 2
        self.fg_color = "black"
        self.bg_color = "red"
        self.button_font = font.Font(size=15)
        self.button_border = 4

        self.JOKES = Jokes.JOKES

        self.support_window = SupportWindow(self)

        self.show_gui()

    def show_gui(self):

        expression_field = tk.Entry(self.parent, bg="white", font=("Calibri", 20),
                                    bd=5, textvariable=self.equation)
        expression_field.grid(columnspan=4, ipadx=145)

        self.equation.set('Enter your expression...')

        button1 = self.create_number_button(number=1)
        button1.grid(row=2, column=0)

        button2 = self.create_number_button(number=2)
        button2.grid(row=2, column=1)

        button3 = self.create_number_button(number=3)
        button3.grid(row=2, column=2)

        button4 = self.create_number_button(number=4)
        button4.grid(row=3, column=0)

        button5 = self.create_number_button(number=5)
        button5.grid(row=3, column=1)

        button6 = self.create_number_button(number=6)
        button6.grid(row=3, column=2)

        button7 = self.create_number_button(number=7)
        button7.grid(row=4, column=0)

        button8 = self.create_number_button(number=8)
        button8.grid(row=4, column=1)

        button9 = self.create_number_button(number=9)
        button9.grid(row=4, column=2)

        button0 = self.create_number_button(number=0)
        button0.grid(row=5, column=0)

        plus = self.create_operator_button(operator="+")
        plus.grid(row=2, column=3)

        minus = self.create_operator_button(operator="-")
        minus.grid(row=3, column=3)

        multiply = self.create_operator_button(operator="*")
        multiply.grid(row=4, column=3)

        divide = self.create_operator_button(operator="/")
        divide.grid(row=5, column=3)

        equal = self.create_button("=", command=self.equalpress)
        equal.grid(row=5, column=2)

        clear = self.create_button("Clear", command=self.clear)
        clear.grid(row=5, column='1')

        pi = self.create_button("pi", command=lambda: self.press(3.141592653589793))
        pi.grid(row=6, column=0)

        Decimal = self.create_operator_button(operator=".")
        Decimal.grid(row=6, column=1)

        support = self.create_button("SUPPORT", command=self.show_support, bg_color="orange")
        support.grid(row=6, column=2)

        joke = self.create_button("JOKE", command=self.tell_joke, bg_color="orange")
        joke.grid(row=6, column=3)

    def press(self, num):
        self.expression = self.expression + str(num)
        self.equation.set(self.expression)

    def equalpress(self):
        try:
            total = str(eval(self.expression))
            self.equation.set(total)
            self.expression = total
        except Exception:
            self.equation.set("error")
            self.expression = ""

    def clear(self):
        self.expression = ""
        self.equation.set("")

    def tell_joke(self):
        print("joke")
        joke = random.choice(self.JOKES)
        messagebox.showinfo("'Joke'", joke)

    def show_support(self):
        print("showing support")
        self.support_window.show()

    def create_button(self, text, command, bg_color=None, fg_color=None):
        if not fg_color:
            fg_color = self.fg_color
        if not bg_color:
            bg_color = self.bg_color
        return tk.Button(self.parent, text=text, fg=fg_color, bg=bg_color,
                         font=self.button_font, bd=self.button_border,
                         height=self.height_of_buttons, width=self.width_of_buttons,
                         command=command)

    def create_number_button(self, number):
        return tk.Button(self.parent, text=str(number), fg=self.fg_color, bg=self.bg_color,
                         font=self.button_font, bd=self.button_border,
                         height=self.height_of_buttons, width=self.width_of_buttons,
                         command=lambda: self.press(number))

    def create_operator_button(self, operator):
        return tk.Button(self.parent, text=operator, fg=self.fg_color, bg=self.bg_color,
                         font=self.button_font, bd=self.button_border,
                         height=self.height_of_buttons, width=self.width_of_buttons,
                         command=lambda: self.press(operator))


if __name__ == "__main__":
    root = tk.Tk()
    CalculatorGUI(root)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()
