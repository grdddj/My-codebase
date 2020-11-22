import os
import sys
import requests
from datetime import datetime
import pyperclip
from autocorrect import Speller

from config import Config
import chat_logger as logger


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)


def get_ip_address():
    logger.info("HELPERS - Getting the IP address")
    response = requests.get(Config.API_URL_IP)
    ip_address_json = response.json()
    return ip_address_json["ip_address"]


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


def is_date_from_today(dt_object):
    today_dt_object = datetime.now()
    today_morning = datetime(year=today_dt_object.year, month=today_dt_object.month,
                             day=today_dt_object.day, hour=0, second=0)
    message_is_from_today = today_morning < dt_object
    return message_is_from_today


# Helper function to fill a text component with a content in a safe way
# Possible modes: "rewrite" - fill it completely from the scratch,
#   "append" - just appending the specified content to already existing one
def define_text_content(text_component, content_to_fill, mode="rewrite"):
    text_component["state"] = "normal"  # enabling to manipulate the content
    if mode == "rewrite":
        text_component.delete("1.0", "end")  # deleting the whole previous content
    text_component.insert("insert", content_to_fill)  # inserting completely new content
    text_component["state"] = "disabled"  # disabling the content for user manipulation


def define_entry_content(entry_component, content_to_fill):
    entry_component["state"] = "normal"
    entry_component.delete(0, "end")
    entry_component.insert(0, content_to_fill)
    entry_component["state"] = "disabled"


def copy_into_clipboard(message):
    pyperclip.copy(message)


class SpellChecker:
    def __init__(self):
        try:
            self.speller = Speller()
        except Exception as err:
            self.log_exception("Initializing spell checker failed - " + str(err))
        self.previous_message = ""
        self.current_message = ""

    def check_message_only_if_necessary(self, message):
        self.previous_message = self.current_message
        self.current_message = message

        new_is_at_the_end = self.something_new_is_at_the_end()
        same_amount_of_words = self.same_amount_of_full_words()

        if new_is_at_the_end and same_amount_of_words:
            return {"ignored": True}
        else:
            return self.check_the_text_for_errors(self.current_message)

    def same_amount_of_full_words(self):
        space_char = " "
        return self.previous_message.count(space_char) == self.current_message.count(space_char)

    def something_new_is_at_the_end(self):
        return self.previous_message == self.current_message[:-1]

    def check_the_text_for_errors(self, text):
        correct_text = self.speller(text)

        if text == correct_text:
            return {"success": True}

        corrected_words = []

        text_words = text.split(" ")
        correct_words = correct_text.split(" ")
        for original, correct in zip(text_words, correct_words):
            if original != correct:
                corrected_words.append((original, correct))

        return {"success": False, "corrected_words": corrected_words}
